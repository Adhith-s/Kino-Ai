// ==========================================
// KINO AI — Frontend Engine
// ==========================================
const API_BASE =
    location.hostname === "localhost" ||
    location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:8000"
        : "";

// ==========================================
// Cinematic Frame Loader Engine
// ==========================================
const TOTAL_FRAMES = 128;
const FRAME_PATH = "assets/frames/";
const FRAME_FPS = 24;

class CinematicLoader {
    constructor() {
        this.canvas = document.getElementById("frameCanvas");
        this.ctx = this.canvas ? this.canvas.getContext("2d") : null;
        this.frames = [];
        this.currentFrame = 0;
        this.isPlaying = false;
        this.animationId = null;
        this.lastFrameTime = 0;
        this.frameInterval = 1000 / FRAME_FPS;
        this.isLoaded = false;
        this._fakeProgress = 0;

        this.statusMessages = [
            "Scanning cinematic database...",
            "Analyzing narrative patterns...",
            "Computing semantic vectors...",
            "Generating personalized insights...",
            "Rendering recommendations...",
            "Almost there..."
        ];
        this.currentStatusIndex = 0;
        this.statusInterval = null;

        this._preloadFrames();
    }

    _preloadFrames() {
        let loaded = 0;
        for (let i = 1; i <= TOTAL_FRAMES; i++) {
            const img = new Image();
            const paddedIndex = String(i).padStart(3, "0");
            img.src = `${FRAME_PATH}frame_${paddedIndex}.jpg`;
            img.onload = () => {
                loaded++;
                if (loaded === TOTAL_FRAMES) {
                    this.isLoaded = true;
                    console.log("🎬 All cinematic frames loaded!");
                }
            };
            img.onerror = () => {
                loaded++;
                if (loaded === TOTAL_FRAMES && !this.isLoaded) {
                    // Check if at least some frames loaded
                    const validFrames = this.frames.filter(f => f.complete && f.naturalWidth > 0);
                    if (validFrames.length > 10) {
                        this.isLoaded = true;
                        console.log(`🎬 Loaded ${validFrames.length}/${TOTAL_FRAMES} frames`);
                    }
                }
            };
            this.frames.push(img);
        }
    }

    _resizeCanvas() {
        if (!this.canvas) return;
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    _drawFrame(frame) {
        if (!frame || !frame.complete || frame.naturalWidth === 0 || !this.ctx) return;
        this._resizeCanvas();
        const ctx = this.ctx;
        const cW = this.canvas.width, cH = this.canvas.height;
        const iR = frame.naturalWidth / frame.naturalHeight;
        const cR = cW / cH;
        let dW, dH, dX, dY;
        if (cR > iR) { dW = cW; dH = cW / iR; dX = 0; dY = (cH - dH) / 2; }
        else { dH = cH; dW = cH * iR; dX = (cW - dW) / 2; dY = 0; }
        ctx.clearRect(0, 0, cW, cH);
        ctx.drawImage(frame, dX, dY, dW, dH);
    }

    _animate(timestamp) {
        if (!this.isPlaying) return;
        const elapsed = timestamp - this.lastFrameTime;
        if (elapsed >= this.frameInterval) {
            this.lastFrameTime = timestamp - (elapsed % this.frameInterval);
            const frame = this.frames[this.currentFrame];
            if (frame && frame.complete && frame.naturalWidth > 0) {
                this._drawFrame(frame);
            }
            this.currentFrame = (this.currentFrame + 1) % TOTAL_FRAMES;
            const progress = document.getElementById("loaderProgress");
            if (progress && this._fakeProgress < 90) {
                this._fakeProgress += 0.4;
                progress.style.width = `${this._fakeProgress}%`;
            }
        }
        this.animationId = requestAnimationFrame((ts) => this._animate(ts));
    }

    _startStatusRotation() {
        this.currentStatusIndex = 0;
        const statusEl = document.getElementById("aiStatus");
        if (statusEl) statusEl.style.transition = "opacity 0.3s ease";
        this.statusInterval = setInterval(() => {
            this.currentStatusIndex = (this.currentStatusIndex + 1) % this.statusMessages.length;
            if (statusEl) {
                statusEl.style.opacity = "0";
                setTimeout(() => {
                    statusEl.innerText = this.statusMessages[this.currentStatusIndex];
                    statusEl.style.opacity = "1";
                }, 200);
            }
        }, 2000);
    }

    _stopStatusRotation() {
        if (this.statusInterval) { clearInterval(this.statusInterval); this.statusInterval = null; }
    }

    show(initialStatus = "Entering the Cinematic Universe...") {
        const loader = document.getElementById("aiLoader");
        const mainStatus = document.getElementById("loaderStatusMain");
        const progress = document.getElementById("loaderProgress");
        this.currentFrame = 0;
        this._fakeProgress = 0;
        if (progress) progress.style.width = "0%";
        if (mainStatus) mainStatus.innerText = initialStatus;
        loader.classList.remove("hidden", "loader-exiting");
        loader.classList.add("flex", "loader-entering");
        this.isPlaying = true;
        this.lastFrameTime = 0;
        this._animate(0);
        this._startStatusRotation();
        document.body.style.overflow = "hidden";
    }

    hide() {
        const loader = document.getElementById("aiLoader");
        const progress = document.getElementById("loaderProgress");
        const statusEl = document.getElementById("aiStatus");
        const mainStatus = document.getElementById("loaderStatusMain");
        if (progress) progress.style.width = "100%";
        if (mainStatus) mainStatus.innerText = "Recommendations Ready";
        if (statusEl) statusEl.innerText = "Enjoy your picks!";
        this._stopStatusRotation();
        
        // Reduced delays for a snappier feel
        setTimeout(() => {
            this.isPlaying = false;
            if (this.animationId) { cancelAnimationFrame(this.animationId); this.animationId = null; }
            loader.classList.remove("loader-entering");
            loader.classList.add("loader-exiting");
            setTimeout(() => {
                loader.classList.add("hidden");
                loader.classList.remove("flex", "loader-exiting");
                document.body.style.overflow = "";
            }, 400); // Reduced from 800ms
        }, 300); // Reduced from 600ms
    }
}

// Initialize
const cinematicLoader = new CinematicLoader();

// ==========================================
// Unified Loader Toggle
// ==========================================
function toggleLoader(show, status = "") {
    if (show) {
        if (cinematicLoader.isLoaded) {
            cinematicLoader.show(status || "Searching the Cinematic Universe...");
        } else {
            // Fallback: just show a dark overlay with text
            const loader = document.getElementById("aiLoader");
            const mainStatus = document.getElementById("loaderStatusMain");
            if (mainStatus) mainStatus.innerText = status || "Loading...";
            loader.classList.remove("hidden");
            loader.classList.add("flex");
            loader.style.background = "rgba(0,0,0,0.9)";
        }
    } else {
        if (cinematicLoader.isLoaded) {
            cinematicLoader.hide();
        } else {
            const loader = document.getElementById("aiLoader");
            loader.classList.add("hidden");
            loader.classList.remove("flex");
            loader.style.background = "";
        }
    }
}

// ==========================================
// Navigation State
// ==========================================
function setActiveNav(navId) {
    document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.mobile-nav-btn').forEach(el => el.classList.remove('active'));
    document.querySelectorAll(`[data-nav="${navId}"]`).forEach(el => el.classList.add('active'));
}

// ==========================================
// Skeleton Loading UI
// ==========================================
function showSkeletons(targetId, count = 5) {
    const row = document.getElementById(targetId);
    row.innerHTML = "";
    for (let i = 0; i < count; i++) {
        const skeleton = document.createElement("div");
        skeleton.className = "skeleton-card";
        skeleton.style.animationDelay = `${i * 0.15}s`;
        row.appendChild(skeleton);
    }
}

// ==========================================
// Initialization
// ==========================================
window.onload = () => {
    setActiveNav('home');
    showSkeletons("trendingRow", 5);
    
    // Load initial popular movies
    fetchFromAPI("/popular?category=all")
        .then(movies => {
            if (movies && movies.length > 0) {
                renderMovies(movies, "trendingRow");
                updateHero(movies[0]);
            }
        })
        .catch(err => {
            console.error("Initial load failed:", err);
            document.getElementById("trendingRow").innerHTML = 
                '<p class="text-gray-500 text-sm col-span-full">Could not connect to backend. Make sure the server is running.</p>';
        });

    // Navbar scroll effect
    window.addEventListener('scroll', () => {
        const nav = document.getElementById('navbar');
        if (window.scrollY > 50) nav.classList.add('scrolled');
        else nav.classList.remove('scrolled');
    });

    // Canvas resize handler
    window.addEventListener('resize', () => {
        if (cinematicLoader.isPlaying) cinematicLoader._resizeCanvas();
    });
};

// ==========================================
// API Fetch Helper
// ==========================================
async function fetchFromAPI(endpoint) {
    const res = await fetch(`${API_BASE}${endpoint}`);
    if (!res.ok) throw new Error(`API returned ${res.status}`);
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    return data;
}

// ==========================================
// Core Search
// ==========================================
async function searchMovie() {
    const input = document.getElementById("searchInput");
    const query = input.value.trim();
    if (!query) {
        input.classList.add('border-red-600');
        input.focus();
        setTimeout(() => input.classList.remove('border-red-600'), 1000);
        return;
    }

    toggleLoader(true, "Searching...");
    document.getElementById("resultsSectionTitle").innerText = `Results for "${query}"`;
    document.getElementById("resultsSection").classList.remove('hidden');

    try {
        const movies = await fetchFromAPI(`/recommend?query=${encodeURIComponent(query)}`);
        toggleLoader(false);
        renderMovies(movies, "movieRow");
        if (movies.length > 0) updateHero(movies[0]);
        setTimeout(() => {
            document.getElementById("resultsSection").scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, cinematicLoader.isLoaded ? 800 : 100); // Reduced from 1500/200
    } catch (error) {
        console.error("Search failed:", error);
        toggleLoader(false);
        document.getElementById("movieRow").innerHTML = 
            '<p class="text-red-400 text-sm col-span-full">Search failed. Make sure the backend is running on port 8000.</p>';
    }
}

// ==========================================
// Navigation Actions
// ==========================================
function goHome() {
    setActiveNav('home');
    document.getElementById("resultsSection").classList.add('hidden');
    document.getElementById("trendingSectionTitle").innerText = "Top Picks for You";
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    showSkeletons("trendingRow", 5);
    fetchFromAPI("/popular?category=all")
        .then(movies => {
            renderMovies(movies, "trendingRow");
            if (movies.length > 0) updateHero(movies[0]);
        })
        .catch(console.error);
}

function loadCategory(category) {
    setActiveNav(category === 'movies' ? 'movies' : 'series');
    const label = category === 'movies' ? '🎬 Popular Movies' : '📺 Popular Series';
    
    document.getElementById("resultsSection").classList.add('hidden');
    document.getElementById("trendingSectionTitle").innerText = label;
    
    toggleLoader(true, `Loading ${category === 'movies' ? 'Movies' : 'TV Series'}...`);
    
    fetchFromAPI(`/popular?category=${category}`)
        .then(movies => {
            toggleLoader(false);
            renderMovies(movies, "trendingRow");
            if (movies.length > 0) updateHero(movies[0]);
            setTimeout(() => {
                document.getElementById("trendingSection").scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, cinematicLoader.isLoaded ? 1500 : 200);
        })
        .catch(err => {
            console.error(err);
            toggleLoader(false);
        });
}

function loadPopular() {
    setActiveNav('popular');
    document.getElementById("resultsSection").classList.add('hidden');
    document.getElementById("trendingSectionTitle").innerText = "🔥 New & Popular";
    
    toggleLoader(true, "Loading Popular...");
    
    fetchFromAPI("/popular?category=all")
        .then(movies => {
            toggleLoader(false);
            renderMovies(movies, "trendingRow");
            if (movies.length > 0) updateHero(movies[0]);
            setTimeout(() => {
                document.getElementById("trendingSection").scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, cinematicLoader.isLoaded ? 1500 : 200);
        })
        .catch(err => {
            console.error(err);
            toggleLoader(false);
        });
}

function searchByGenre(genre) {
    document.getElementById("searchInput").value = genre;
    document.getElementById("resultsSectionTitle").innerText = `${genre.charAt(0).toUpperCase() + genre.slice(1)} Movies`;
    document.getElementById("resultsSection").classList.remove('hidden');
    
    toggleLoader(true, `Finding ${genre} movies...`);
    
    fetchFromAPI(`/genre?genre=${encodeURIComponent(genre)}`)
        .then(movies => {
            toggleLoader(false);
            renderMovies(movies, "movieRow");
            if (movies.length > 0) updateHero(movies[0]);
            setTimeout(() => {
                document.getElementById("resultsSection").scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, cinematicLoader.isLoaded ? 1500 : 200);
        })
        .catch(err => {
            console.error(err);
            toggleLoader(false);
        });
}

// ==========================================
// Render Movies
// ==========================================
function renderMovies(movies, targetId) {
    const row = document.getElementById(targetId);
    row.innerHTML = "";

    if (!movies || movies.length === 0) {
        row.innerHTML = '<p class="text-gray-500 text-sm col-span-full">No results found.</p>';
        return;
    }

    movies.forEach((movie, index) => {
        const card = document.createElement("div");
        card.className = "movie-card animate-fade-in";
        card.style.animationDelay = `${index * 0.1}s`;

        const matchBadge = movie.match > 0 
            ? `<span class="match-badge">${movie.match}% Match</span>` 
            : '';

        card.innerHTML = `
            <div class="relative aspect-[2/3] overflow-hidden">
                <img src="${movie.poster}" 
                     class="w-full h-full object-cover" 
                     alt="${movie.title}"
                     loading="lazy"
                     onerror="this.src='https://placehold.co/500x750/111111/DC2626?text=${encodeURIComponent(movie.title)}&font=raleway'">
                <div class="absolute inset-0 card-overlay flex flex-col justify-end p-4">
                    ${matchBadge}
                    <h3 class="text-sm font-bold text-white mb-1 mt-2">${movie.title}</h3>
                    <p class="text-[10px] text-gray-400 line-clamp-2 italic">${movie.explanation || movie.overview || ''}</p>
                </div>
            </div>
        `;

        card.onclick = () => updateHero(movie);
        row.appendChild(card);
    });
}

// ==========================================
// Hero Update
// ==========================================
function updateHero(movie) {
    const hero = document.getElementById("hero");
    const heroTitle = document.getElementById("heroTitle");
    const heroDesc = document.getElementById("heroDesc");
    const heroMatch = document.getElementById("heroMatch");

    hero.style.backgroundImage = `url(${movie.poster})`;
    heroTitle.innerText = movie.title;
    heroDesc.innerText = movie.explanation || movie.overview || "Discover this cinematic masterpiece with KINO AI.";
    
    if (movie.match > 0) {
        heroMatch.innerText = `${movie.match}% Match`;
        heroMatch.classList.remove('hidden');
    } else {
        heroMatch.classList.add('hidden');
    }
}

// ==========================================
// Enter Key Support
// ==========================================
document.getElementById("searchInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") searchMovie();
});