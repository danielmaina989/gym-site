document.addEventListener("DOMContentLoaded", function () {
    function handleMembershipSelection(form, planType) {
        console.log("Selected Plan:", planType);
        console.log("Current Membership:", currentMembership);

        if (currentMembership && currentMembership.toLowerCase() === planType.toLowerCase()) {
            // Renewal Swal
            Swal.fire({
                icon: "info",
                title: "Renew Membership",
                text: `You're already subscribed to the ${planType} membership. Would you like to renew for another month?`,
                confirmButtonText: "Renew Now",
                confirmButtonColor: "#FFA500",
                showCancelButton: true,
                cancelButtonText: "Cancel",
                cancelButtonColor: "#d33"
            }).then((result) => {
                if (result.isConfirmed) {
                    form.submit();  // 🔥 This now allows Stripe redirection!
                }
            });
            return;
        } else {
            // Upgrade Swal
            Swal.fire({
                icon: "warning",
                title: "Confirm Upgrade",
                text: `Are you sure you want to switch to the ${planType} membership?`,
                confirmButtonText: "Yes, Upgrade",
                cancelButtonText: "Cancel",
                confirmButtonColor: "#28a745",
                cancelButtonColor: "#d33",
                showCancelButton: true
            }).then((result) => {
                if (result.isConfirmed) {
                    form.submit();  // 🔥 Proceed to Stripe if confirmed
                }
            });
        }
    }

    // Attach event listeners to membership upgrade forms
    document.querySelectorAll(".membership-upgrade-form").forEach(form => {
        form.addEventListener("submit", function (event) {
            event.preventDefault(); // Prevent default form submission
            const planType = this.getAttribute("data-plan-type");
            handleMembershipSelection(this, planType);  // Pass form reference
        });
    });
});
