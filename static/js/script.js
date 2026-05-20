document.addEventListener("DOMContentLoaded", function () {
    console.log("VELORA luxury experience loaded.");

    const navbar = document.querySelector(".navbar");
    // const wishlistButtons = document.querySelectorAll(".wishlist-btn");
    const searchForm = document.querySelector(".search-box");
    const cartIcon = document.querySelector(".cart-icon");
    const productCards = document.querySelectorAll(".product-card");

    // Navbar scroll effect
    window.addEventListener("scroll", function () {
        if (window.scrollY > 20) {
            navbar.classList.add("navbar-scrolled");
        } else {
            navbar.classList.remove("navbar-scrolled");
        }
    });

    // Add scroll reveal classes automatically
    const revealElements = document.querySelectorAll(
        ".section, .service-strip, .promo-grid, .product-card, .category-card, .collection-card"
    );

    revealElements.forEach(function (element) {
        element.classList.add("reveal-on-scroll");
    });

    const revealObserver = new IntersectionObserver(
        function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("visible");
                    revealObserver.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.12,
        }
    );

    revealElements.forEach(function (element) {
        revealObserver.observe(element);
    });

    // Wishlist heart toggle
    // wishlistButtons.forEach(function (button) {
    //     button.addEventListener("click", function (event) {
    //         event.preventDefault();
    //         event.stopPropagation();

    //         const icon = button.querySelector("i");

    //         if (icon.classList.contains("fa-regular")) {
    //             icon.classList.remove("fa-regular");
    //             icon.classList.add("fa-solid");
    //             button.classList.add("active-wishlist");
    //             showToast("Added to wishlist");
    //         } else {
    //             icon.classList.remove("fa-solid");
    //             icon.classList.add("fa-regular");
    //             button.classList.remove("active-wishlist");
    //             showToast("Removed from wishlist");
    //         }
    //     });
    // });

    // Search validation
    // if (searchForm) {
    //     searchForm.addEventListener("submit", function (event) {
    //         const searchInput = searchForm.querySelector("input");
    //         const query = searchInput.value.trim();

    //         if (query === "") {
    //             event.preventDefault();
    //             showToast("Type something stylish first");
    //             return;
    //         }

    //         event.preventDefault();
    //         showToast("Search backend will be connected next");
    //     });
    // }
    if (searchForm) {
    searchForm.addEventListener("submit", function (event) {
        const searchInput = searchForm.querySelector("input");
        const query = searchInput.value.trim();

        if (query === "") {
            event.preventDefault();
            showToast("Type something to search");
        }
    });
}

    // Temporary cart action
    // if (cartIcon) {
    //     cartIcon.addEventListener("click", function (event) {
    //         event.preventDefault();
    //         showToast("Cart backend will be connected next");
    //     });
    // }

    // Product click temporary action
    // productCards.forEach(function (card) {
    //     card.addEventListener("click", function () {
    //         showToast("Product detail page coming next");
    //     });
    // });

    // Luxury cursor glow on desktop
    if (window.innerWidth > 768) {
        const cursorGlow = document.createElement("div");
        cursorGlow.className = "cursor-glow";
        document.body.appendChild(cursorGlow);

        document.addEventListener("mousemove", function (event) {
            cursorGlow.style.left = event.clientX + "px";
            cursorGlow.style.top = event.clientY + "px";
            cursorGlow.style.opacity = "1";
        });

        document.addEventListener("mouseleave", function () {
            cursorGlow.style.opacity = "0";
        });
    }

    // Toast function
    function showToast(message) {
        let toast = document.querySelector(".velora-toast");

        if (!toast) {
            toast = document.createElement("div");
            toast.className = "velora-toast";
            document.body.appendChild(toast);
        }

        toast.textContent = message;
        toast.classList.add("show-toast");

        setTimeout(function () {
            toast.classList.remove("show-toast");
        }, 2200);
    }

    // Product detail image switcher
const thumbButtons = document.querySelectorAll(".thumb-img");
const mainProductImage = document.querySelector("#mainProductImage");

if (thumbButtons.length && mainProductImage) {
    thumbButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const newImage = button.getAttribute("data-image");

            mainProductImage.src = newImage;

            thumbButtons.forEach(function (item) {
                item.classList.remove("active-thumb");
            });

            button.classList.add("active-thumb");
        });
    });
}

// Profile dropdown
const profileToggle = document.getElementById("profileToggle");
const profileDropdown = document.getElementById("profileDropdown");

if (profileToggle && profileDropdown) {
    profileToggle.addEventListener("click", function (event) {
        event.stopPropagation();
        profileDropdown.classList.toggle("show");
    });

    profileDropdown.addEventListener("click", function (event) {
        event.stopPropagation();
    });

    document.addEventListener("click", function () {
        profileDropdown.classList.remove("show");
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            profileDropdown.classList.remove("show");
        }
    });
}
});

