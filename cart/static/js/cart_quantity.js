document.addEventListener("DOMContentLoaded", function () {
    const quantityInputs = document.querySelectorAll(".quantity-input");

    quantityInputs.forEach(input => {
        input.addEventListener("change", function () {
            const productId = this.dataset.productId;
            const newQuantity = this.value;

            if (newQuantity < 1) return; // Prevent negative or zero quantity

            fetch(`/cart/update/${productId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({ quantity: newQuantity })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById(`subtotal-${productId}`).textContent = `$${data.subtotal}`;
                    document.getElementById("cart-total").textContent = data.total;
                }
            })
            .catch(error => console.error("Error:", error));
        });
    });

    // ✅ CSRF Token Function
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
