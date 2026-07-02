"""Custom web UI for the renovation agent."""

from __future__ import annotations

import mimetypes
import sys
import uuid
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from google.adk.runners import InMemoryRunner
from google.genai import types

load_dotenv()

from renovation_agent import root_agent  # noqa: E402

APP_NAME = "renovation_agent"
STATIC_DIR = Path(__file__).parent / "static"

runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
sessions: dict[str, str] = {}

app = FastAPI(title="Home Renovation Planner")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    return HTMLResponse((STATIC_DIR / "index.html").read_text(encoding="utf-8"))


async def _list_artifact_keys(user_id: str, session_id: str) -> set[str]:
    keys = await runner.artifact_service.list_artifact_keys(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    return set(keys)


async def _load_artifact_bytes(user_id: str, session_id: str, filename: str) -> tuple[bytes, str] | None:
    part = await runner.artifact_service.load_artifact(
        app_name=APP_NAME,
        user_id=user_id,
        filename=filename,
        session_id=session_id,
    )
    if not part or not part.inline_data or not part.inline_data.data:
        return None
    mime = part.inline_data.mime_type or "image/png"
    return part.inline_data.data, mime


def _is_image_artifact(filename: str) -> bool:
    lower = filename.lower()
    return lower.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif"))


@app.post("/api/chat")
async def chat(
    message: str = Form(...),
    session_id: str | None = Form(default=None),
    images: list[UploadFile] = File(default=[]),
) -> JSONResponse:
    message = message.strip()
    if not message and not images:
        raise HTTPException(status_code=400, detail="Enter a message or upload an image.")

    user_id = "web_user"
    if not session_id or session_id not in sessions:
        session_id = str(uuid.uuid4())
        await runner.session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        sessions[session_id] = user_id

    before_artifacts = await _list_artifact_keys(user_id, session_id)

    parts: list[types.Part] = []
    if message:
        parts.append(types.Part(text=message))

    for upload in images:
        if not upload.filename:
            continue
        data = await upload.read()
        if not data:
            continue
        mime = upload.content_type or mimetypes.guess_type(upload.filename)[0] or "image/jpeg"
        parts.append(
            types.Part(
                inline_data=types.Blob(
                    mime_type=mime,
                    data=data,
                    display_name=upload.filename,
                )
            )
        )

    if not parts:
        raise HTTPException(status_code=400, detail="Nothing to send.")

    user_content = types.Content(role="user", parts=parts)
    response_chunks: list[str] = []
    seen_text: set[str] = set()

    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_content,
        ):
            if not event.content or not event.content.parts:
                continue
            for part in event.content.parts:
                if part.function_call or part.function_response:
                    continue
                if part.text:
                    text = part.text.strip()
                    if text and text not in seen_text:
                        seen_text.add(text)
                        response_chunks.append(text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    after_artifacts = await _list_artifact_keys(user_id, session_id)
    new_artifacts = sorted(after_artifacts - before_artifacts)

    output_images: list[dict[str, str]] = []
    for filename in new_artifacts:
        if _is_image_artifact(filename):
            output_images.append(
                {
                    "filename": filename,
                    "url": f"/api/artifacts/{session_id}/{filename}",
                }
            )

    # Also surface the latest renovation rendering if no new artifact diff was found.
    if not output_images:
        rendering_candidates = sorted(
            [name for name in after_artifacts if "renovation" in name.lower() and _is_image_artifact(name)]
        )
        if rendering_candidates:
            latest = rendering_candidates[-1]
            output_images.append(
                {
                    "filename": latest,
                    "url": f"/api/artifacts/{session_id}/{latest}",
                }
            )

    return JSONResponse(
        {
            "session_id": session_id,
            "text": "\n\n".join(response_chunks) if response_chunks else "Done.",
            "images": output_images,
        }
    )


@app.get("/api/artifacts/{session_id}/{filename}")
async def get_artifact(session_id: str, filename: str) -> FileResponse:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    user_id = sessions[session_id]
    loaded = await _load_artifact_bytes(user_id, session_id, filename)
    if not loaded:
        raise HTTPException(status_code=404, detail="Artifact not found.")

    data, mime = loaded
    temp_path = STATIC_DIR / "_cache"
    temp_path.mkdir(exist_ok=True)
    cache_file = temp_path / f"{session_id}_{filename.replace('/', '_')}"
    cache_file.write_bytes(data)
    return FileResponse(cache_file, media_type=mime)


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=3001, reload=False)


if __name__ == "__main__":
    main()
