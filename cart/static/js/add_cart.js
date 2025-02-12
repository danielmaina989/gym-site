document.addEventListener("DOMContentLoaded", function () {
    const addToCartButtons = document.querySelectorAll(".add-to-cart-btn");

    addToCartButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const productId = this.dataset.productId;

            fetch(`/cart/add/${productId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "Content-Type": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    Swal.fire({
                        title: "Success!",
                        text: data.message,
                        icon: "success",
                        confirmButtonText: "OK"  // ✅ Add "OK" button
                    });

                    // Update cart count dynamically
                    document.getElementById("cart-count").textContent = data.cart_count;
                } else {
                    Swal.fire({
                        title: "Error!",
                        text: data.error,
                        icon: "error"
                    });
                }
            })
            .catch(error => console.error("Error:", error));
        });
    });

    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
    }
});
