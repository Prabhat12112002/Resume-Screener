document.addEventListener("DOMContentLoaded", () => {
    // ── DOM References ────────────────────────────────────────────────
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("file-input");
    const fileListContainer = document.getElementById("file-list-container");
    const fileList = document.getElementById("file-list");
    const fileCount = document.getElementById("file-count");
    
    const jobDescription = document.getElementById("job-description");
    const screenBtn = document.getElementById("screen-btn");
    const spinner = screenBtn.querySelector(".spinner");
    const btnText = screenBtn.querySelector(".btn-text");
    
    const resultsPlaceholder = document.getElementById("results-placeholder");
    const resultsCount = document.getElementById("results-count");
    const resultsList = document.getElementById("results-list");
    
    const toast = document.getElementById("toast");

    // ── State ─────────────────────────────────────────────────────────
    let uploadedFiles = [];

    // ── Drag & Drop Event Listeners ──────────────────────────────────
    dropzone.addEventListener("click", () => fileInput.click());
    
    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });
    
    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dragover");
    });
    
    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener("change", (e) => {
        handleFiles(e.target.files);
    });

    // ── File Management ───────────────────────────────────────────────
    function handleFiles(files) {
        for (let file of files) {
            const ext = file.name.split('.').pop().toLowerCase();
            if (ext !== 'pdf' && ext !== 'txt') {
                showToast("Only PDF and TXT resumes are supported.", "error");
                continue;
            }
            // Avoid duplicate file names
            if (uploadedFiles.some(f => f.name === file.name)) {
                showToast(`"${file.name}" has already been selected.`, "warning");
                continue;
            }
            uploadedFiles.push(file);
        }
        updateFileList();
    }

    function updateFileList() {
        fileList.innerHTML = "";
        
        if (uploadedFiles.length === 0) {
            fileListContainer.style.display = "none";
            fileCount.textContent = "0";
            return;
        }

        fileListContainer.style.display = "block";
        fileCount.textContent = uploadedFiles.length;

        uploadedFiles.forEach((file, index) => {
            const li = document.createElement("li");
            li.className = "file-item";
            
            const fileMeta = document.createElement("div");
            fileMeta.className = "file-item-name";
            fileMeta.innerHTML = `📄 <span>${file.name}</span>`;
            
            const removeBtn = document.createElement("button");
            removeBtn.className = "file-item-remove";
            removeBtn.innerHTML = "&times;";
            removeBtn.addEventListener("click", () => removeFile(index));

            li.appendChild(fileMeta);
            li.appendChild(removeBtn);
            fileList.appendChild(li);
        });
    }

    function removeFile(index) {
        uploadedFiles.splice(index, 1);
        updateFileList();
    }

    // ── Toast Notifications ───────────────────────────────────────────
    function showToast(message, type = "success") {
        toast.className = `notification-toast ${type}`;
        toast.textContent = message;
        toast.style.display = "flex";
        
        setTimeout(() => {
            toast.style.display = "none";
        }, 4000);
    }

    // ── Submit Handling ──────────────────────────────────────────────
    screenBtn.addEventListener("click", async () => {
        const jd = jobDescription.value.trim();
        
        if (!jd) {
            showToast("Please enter a Job Description.", "error");
            return;
        }
        if (uploadedFiles.length === 0) {
            showToast("Please upload at least one resume.", "error");
            return;
        }

        // Lock button UI state
        screenBtn.disabled = true;
        spinner.style.display = "block";
        btnText.textContent = "Analyzing Resumes...";

        const formData = new FormData();
        formData.append("job_description", jd);
        
        uploadedFiles.forEach(file => {
            formData.append("resumes", file);
        });

        try {
            const response = await fetch("/screen-resumes", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to screen resumes.");
            }

            const data = await response.json();
            renderResults(data);
            showToast("Resume screening completed successfully!", "success");

        } catch (err) {
            showToast(err.message, "error");
        } finally {
            // Unlock button UI state
            screenBtn.disabled = false;
            spinner.style.display = "none";
            btnText.textContent = "Run Smart Screening";
        }
    });

    // ── Rendering Results ────────────────────────────────────────────
    function renderResults(data) {
        resultsPlaceholder.style.display = "none";
        resultsCount.style.display = "block";
        resultsCount.textContent = `${data.total_resumes} Resumes`;
        resultsList.innerHTML = "";

        data.results.forEach((res, index) => {
            // Determine progress ring coloring
            let strokeColor = "var(--accent-danger)";
            if (res.match_score >= 80) strokeColor = "var(--accent-success)";
            else if (res.match_score >= 40) strokeColor = "var(--accent-warning)";

            // Calculate SVG dashoffset
            const radius = 36;
            const circumference = 2 * Math.PI * radius;
            const offset = circumference - (res.match_score / 100) * circumference;

            // Generate tags
            const matchedTags = res.matched_skills.map(s => `<span class="tag matched">${s}</span>`).join("");
            const missingTags = res.missing_skills.map(s => `<span class="tag missing">${s}</span>`).join("");

            // Determine if Groq matched or local fallback
            const isGroq = res.engine === "groq";
            const engineTag = isGroq ? 
                `<span class="engine-tag groq">Groq AI</span>` : 
                `<span class="engine-tag local">Local Match</span>`;

            const card = document.createElement("div");
            card.className = "glass-card result-card";
            card.style.animationDelay = `${index * 0.1}s`;

            card.innerHTML = `
                <div class="score-circle-container">
                    <svg class="score-svg" width="80" height="80">
                        <circle class="score-circle-bg" cx="40" cy="40" r="${radius}"></circle>
                        <circle class="score-circle-bar" cx="40" cy="40" r="${radius}" 
                            style="stroke: ${strokeColor}; stroke-dashoffset: ${offset};"></circle>
                    </svg>
                    <div class="score-text">${res.match_score}</div>
                </div>
                <div class="result-info">
                    <div class="result-meta">
                        <h3 class="candidate-name">${res.name}</h3>
                        ${engineTag}
                    </div>
                    <p class="explanation-text">${res.explanation}</p>
                    
                    ${res.matched_skills.length > 0 ? `
                        <div class="skills-block">
                            <span class="skills-label">Matched Skills</span>
                            <div class="skills-tags">${matchedTags}</div>
                        </div>
                    ` : ""}
                    
                    ${res.missing_skills.length > 0 ? `
                        <div class="skills-block">
                            <span class="skills-label">Missing Skills</span>
                            <div class="skills-tags">${missingTags}</div>
                        </div>
                    ` : ""}
                </div>
            `;

            resultsList.appendChild(card);
        });
    }
});
