// Toggle the visibility of a dropdown menu
const toggleDropdown = (dropdown, menu, isOpen) => {
  dropdown.classList.toggle("open", isOpen);
  menu.style.height = isOpen ? `${menu.scrollHeight}px` : 0;
};
// Close all open dropdowns
const closeAllDropdowns = () => {
  document.querySelectorAll(".dropdown-container.open").forEach((openDropdown) => {
    toggleDropdown(openDropdown, openDropdown.querySelector(".dropdown-menu"), false);
  });
};
// Attach click event to all dropdown toggles
document.querySelectorAll(".dropdown-toggle").forEach((dropdownToggle) => {
  dropdownToggle.addEventListener("click", (e) => {
    e.preventDefault();
    const dropdown = dropdownToggle.closest(".dropdown-container");
    const menu = dropdown.querySelector(".dropdown-menu");
    const isOpen = dropdown.classList.contains("open");
    closeAllDropdowns(); // Close all open dropdowns
    toggleDropdown(dropdown, menu, !isOpen); // Toggle current dropdown visibility
  });
});
    const sidebar = document.querySelector(".sidebar");
    const sidebarToggler = document.querySelector(".sidebar-toggler");
    const menuToggler = document.querySelector(".menu-toggler");
    // Ensure these heights match the CSS sidebar height values
    let collapsedSidebarHeight = "56px"; // Height in mobile view (collapsed)
    let fullSidebarHeight = "calc(100vh - 32px)"; // Height in larger screen
    // Toggle sidebar's collapsed state
    sidebarToggler.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
      document.body.classList.toggle('sidebar-collapsed');
    });
    // Update sidebar height and menu toggle text
    const toggleMenu = (isMenuActive) => {
      sidebar.style.height = isMenuActive ? `${sidebar.scrollHeight}px` : collapsedSidebarHeight;
      menuToggler.querySelector("span").innerText = isMenuActive ? "close" : "menu";
    }
    // Toggle menu-active class and adjust height
    menuToggler.addEventListener("click", () => {
      toggleMenu(sidebar.classList.toggle("menu-active"));
    });
    // (Optional code): Adjust sidebar height on window resize
    window.addEventListener("resize", () => {
      if (window.innerWidth >= 1024) {
        sidebar.style.height = fullSidebarHeight;
      } else {
        sidebar.classList.remove("collapsed");
        sidebar.style.height = "auto";
        toggleMenu(sidebar.classList.contains("menu-active"));
      }
    });

usedSpareparts = usedSpareparts.map(up => ({ id: up[0], nama: up[1], qty: up[2] }));
allSpareparts = allSpareparts.map(as => ({ id: as[0], nama: as[1] }));

function addRow(){
    let table = document.getElementById("selectedSparepartTable").getElementsByTagName('tbody')[0];
    let rowCount = table.rows.length;
    let row = table.insertRow(rowCount);

    row.innerHTML = `
        <td>${rowCount + 1}</td>
        <td><input type="text" name="id" onkeyup="searchTable(event, this)"></td>
        <td><input type="text" name="nama" onkeyup="searchTable(event, this)"></td>
        <td><input type="number" min="1"></td>
        <td class="remove-btn" onclick="removeRow(this)">❌</td>
    `;
}