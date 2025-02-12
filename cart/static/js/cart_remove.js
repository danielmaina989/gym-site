document.addEventListener("DOMContentLoaded", function () {
    const removeButtons = document.querySelectorAll(".remove-from-cart-btn");

    removeButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const productId = this.dataset.productId;

            Swal.fire({
                title: "Are you sure?",
                text: "Do you want to remove this item from your cart?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d33",
                cancelButtonColor: "#3085d6",
                confirmButtonText: "Yes, remove it!"
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/cart/remove/${productId}/`, {
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
                                title: "Removed!",
                                text: data.message,
                                icon: "success",
                                confirmButtonText: "OK"
                            }).then(() => {
                                location.reload(); // 🔄 Reload the page after item is removed
                            });
                        } else {
                            Swal.fire({
                                title: "Error!",
                                text: data.error,
                                icon: "error"
                            });
                        }
                    })
                    .catch(error => console.error("Error:", error));
                }
            });
        });
    });

    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
    }
});
