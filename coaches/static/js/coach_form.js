// Show resume field only if specialization is 'Nutritionist'
document.addEventListener('DOMContentLoaded', function () {
    const specializationField = document.getElementById('id_specialization');
    const resumeField = document.getElementById('resume-field');

    const toggleResumeField = () => {
        if (specializationField.value === 'Nutritionist') {
            resumeField.style.display = 'block';
        } else {
            resumeField.style.display = 'none';
        }
    };

    // Trigger the function on page load and when the specialization changes
    toggleResumeField();
    specializationField.addEventListener('change', toggleResumeField);
});
