function loadEnrollmentHistory(beneficiaryId) {
  fetch(`get_enrollments.php?id=${beneficiaryId}`)
    .then(res => res.json())
    .then(data => {
      const tbody = document.querySelector('#enrollment_history tbody');
      tbody.innerHTML = '';
      data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${row.name}</td>
          <td>${row.status}</td>
          <td>${row.enrollment_date}</td>
        `;
        if (sessionStorage.getItem('role') === 'manager' && row.status === 'Pending') {
          const approveBtn = document.createElement('button');
          approveBtn.textContent = 'Approve';
          approveBtn.onclick = () => updateStatus(row.enrollment_id, 'Approved');

          const rejectBtn = document.createElement('button');
          rejectBtn.textContent = 'Reject';
          rejectBtn.onclick = () => updateStatus(row.enrollment_id, 'Rejected');

          const td = document.createElement('td');
          td.appendChild(approveBtn);
          td.appendChild(rejectBtn);
          tr.appendChild(td);
        }
        tbody.appendChild(tr);
      });
    });
}
