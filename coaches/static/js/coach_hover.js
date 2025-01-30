
  // Add hover effect to show booking overlay
  document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('mouseover', () => {
      card.querySelector('.booking-overlay').classList.remove('d-none');
    });
    card.addEventListener('mouseout', () => {
      card.querySelector('.booking-overlay').classList.add('d-none');
    });
  });