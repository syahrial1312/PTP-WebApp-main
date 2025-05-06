spareparts = spareparts.map(sp => ({ id: sp[0], name: sp[1] }));
let selectedSpareparts = [];

function addToSelected(id, name) {
  let table = document.getElementById("selectedSparepartTable").getElementsByTagName("tbody")[0];
  // Cek apakah sparepart sudah ada, jika ada tambahkan qty
  let existingRow = [...table.rows].find(row => row.cells[1].innerText === id);
  if (existingRow) {
      let qtyInput = existingRow.cells[3].querySelector("input");
      qtyInput.value = parseInt(qtyInput.value) + 1;
      return;
  }
  let rowCount = table.rows.length;
  let row = table.insertRow(rowCount);
  row.innerHTML = `
      <td>${rowCount + 1}</td>
      <td><input type="hidden" name="sparepart_id[]" value="${id}">${id}</td>
      <td>${name}</td>
      <td><input type="number" name="sparepart_qty[]" value="1" min="1"></td>
      <td style="color: red; cursor: pointer;" onclick="removeRow(this)">❌</td>
  `;
}

// function addToSelected(id, name) {
//   let table = document
//     .getElementById("selectedSparepartTable")
//     .getElementsByTagName("tbody")[0];

//   // Cek apakah sparepart sudah ada, jika ada tambahkan qty
//   let existingRow = [...table.rows].find(
//     (row) => row.cells[1].innerText === id
//   );
//   if (existingRow) {
//     let qtyInput = existingRow.cells[3].querySelector("input");
//     qtyInput.value = parseInt(qtyInput.value) + 1;
//     return;
//   }

//   let rowCount = table.rows.length;
//   let row = table.insertRow(rowCount);

//   row.innerHTML = `
//             <td>${rowCount + 1}</td>
//             <td><input type="text" value="${id}" readonly></td>
//             <td><input type="text" value="${name}" readonly></td>
//             <td><input type="number" value="1" min="1" oninput="validateQty(this)"></td>
//             <td style="color: red; cursor: pointer;" onclick="removeRow(this)">❌</td>
//         `;
// }

function removeRow(button) {
  let row = button.parentNode;
  row.parentNode.removeChild(row);
  updateRowNumbers();
}

function updateRowNumbers() {
  let rows = document.querySelectorAll("#selectedSparepartTable tbody tr");
  rows.forEach((row, index) => {
    row.cells[0].innerText = index + 1;
  });
}

function validateQty(input) {
  if (input.value < 1 || input.value === "") {
    input.value = null;
  }
}

function searchTable() {
  let input = document.getElementById("searchBar").value.toLowerCase();
  let tableBody = document.getElementById("databaseBody");
  let databaseTable = document.getElementById("databaseSparepartTable");
  let databaseTitle = document.getElementById("databaseTitle");

  if (input === "") {
    databaseTable.style.display = "none";
    databaseTitle.style.display = "none";
    return;
  }

  let filteredSpareparts = spareparts.filter(
    (sparepart) =>
    //   sparepart.id.toLowerCase().includes(input) ||
      sparepart.name.toLowerCase().includes(input)
  );

  tableBody.innerHTML = "";
  filteredSpareparts.forEach((sparepart) => {
    let row = tableBody.insertRow();
    row.innerHTML = `
                <td>${sparepart.id}</td>
                <td>${sparepart.name}</td>
                <td><button type="button" class="add-btn" onclick="addToSelected('${sparepart.id}', '${sparepart.name}')">Add</button></td>
            `;
  });

  databaseTable.style.display = "table";
  databaseTitle.style.display = "block";
}
