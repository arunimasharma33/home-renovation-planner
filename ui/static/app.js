const messageEl = document.getElementById("message");
const imagesEl = document.getElementById("images");
const pickImagesBtn = document.getElementById("pick-images");
const dropzone = document.getElementById("dropzone");
const fileListEl = document.getElementById("file-list");
const submitBtn = document.getElementById("submit");
const resetBtn = document.getElementById("reset");
const outputEl = document.getElementById("output");
const statusEl = document.getElementById("status");

let sessionId = localStorage.getItem("renovation_session_id") || null;
let selectedFiles = [];

function setStatus(text, kind = "idle") {
  statusEl.textContent = text;
  statusEl.className = `status ${kind}`;
}

function renderFileList() {
  fileListEl.innerHTML = "";
  selectedFiles.forEach((file) => {
    const item = document.createElement("li");
    item.textContent = file.name;
    fileListEl.appendChild(item);
  });
}

function addFiles(files) {
  for (const file of files) {
    if (file.type.startsWith("image/")) {
      selectedFiles.push(file);
    }
  }
  renderFileList();
}

pickImagesBtn.addEventListener("click", () => imagesEl.click());
imagesEl.addEventListener("change", () => {
  addFiles(imagesEl.files);
  imagesEl.value = "";
});

dropzone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropzone.style.borderColor = "#2f6b4f";
});

dropzone.addEventListener("dragleave", () => {
  dropzone.style.borderColor = "#c9bfb3";
});

dropzone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropzone.style.borderColor = "#c9bfb3";
  addFiles(event.dataTransfer.files);
});

function renderOutput(data) {
  outputEl.classList.remove("empty");
  outputEl.innerHTML = "";

  const textBlock = document.createElement("div");
  textBlock.className = "output-text";
  textBlock.textContent = data.text || "No text response.";
  outputEl.appendChild(textBlock);

  if (data.images?.length) {
    const gallery = document.createElement("div");
    gallery.className = "output-images";

    data.images.forEach((image) => {
      const figure = document.createElement("figure");
      const img = document.createElement("img");
      img.src = `${image.url}?t=${Date.now()}`;
      img.alt = image.filename;
      const caption = document.createElement("figcaption");
      caption.textContent = image.filename;
      figure.appendChild(img);
      figure.appendChild(caption);
      gallery.appendChild(figure);
    });

    outputEl.appendChild(gallery);
  }
}

async function sendMessage() {
  const message = messageEl.value.trim();
  if (!message && selectedFiles.length === 0) {
    setStatus("Add a message or image", "error");
    return;
  }

  submitBtn.disabled = true;
  setStatus("Planning...", "loading");

  const formData = new FormData();
  formData.append("message", message || "Please analyze the uploaded image(s).");
  if (sessionId) {
    formData.append("session_id", sessionId);
  }
  selectedFiles.forEach((file) => formData.append("images", file));

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Request failed");
    }

    sessionId = data.session_id;
    localStorage.setItem("renovation_session_id", sessionId);
    renderOutput(data);
    setStatus("Done", "idle");
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    submitBtn.disabled = false;
  }
}

submitBtn.addEventListener("click", sendMessage);

resetBtn.addEventListener("click", () => {
  sessionId = null;
  localStorage.removeItem("renovation_session_id");
  selectedFiles = [];
  renderFileList();
  messageEl.value = "";
  outputEl.classList.add("empty");
  outputEl.innerHTML = "<p>Your renovation plan and renderings will appear here.</p>";
  setStatus("Ready", "idle");
});

messageEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    sendMessage();
  }
});
