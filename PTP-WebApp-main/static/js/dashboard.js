const bulanLabel = [
  "", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
  "Jul", "Agu", "Sep", "Okt", "Nov", "Des"
];
sparepart= mostUseSparepart.map(item=> item[0])
jumlahSparepart= mostUseSparepart.map(item=> item[1])
woPerMonth = woPerMonth.map(wopm => ({bulan: wopm[0], jumlah: wopm[1]}))
bulan=woPerMonth.map(item=> bulanLabel[item.bulan]  )
jumlahWo=woPerMonth.map(item=> item.jumlah)
mesin=brokenMachine.map(item=> item[0])
jumlahMesin=brokenMachine.map(item=> item[1])

const woChart = document.getElementById("woChart").getContext("2d");
const sparepartChart = document.getElementById("sparepartChart").getContext("2d");
const machineChart = document.getElementById("machineChart").getContext("2d");
// Warna gradasi untuk tiap bar
const colorStart = [
  "#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6",
  "#1abc9c", "#e67e22", "#34495e", "#7f8c8d", "#ff9ff3",
  "#00cec9", "#d63031"
];

const warnaWoChart = jumlahWo.map((_, i) => {
  const gradient = woChart.createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, colorStart[i % colorStart.length]);
  gradient.addColorStop(1, "#000");
  return gradient;
});
const warnaSparepartChart = jumlahWo.map((_, i) => {
  const gradient = sparepartChart.createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, colorStart[i % colorStart.length]);
  gradient.addColorStop(1, "#000");
  return gradient;
});
const warnaMesinChart = jumlahWo.map((_, i) => {
  const gradient = machineChart.createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, colorStart[i % colorStart.length]);
  gradient.addColorStop(1, "#000");
  return gradient;
});

new Chart(woChart, {
  type: "bar",
  data: {
    labels: bulan,
    datasets: [{
      label: "Jumlah Laporan",
      data: jumlahWo,
      backgroundColor: colorStart,
      hoverBackgroundColor: "#1abc9c",
      borderRadius: 8,
      barPercentage: 0.6,
      categoryPercentage: 0.8
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: 10
    },
    interaction: {
      mode: 'index',
      intersect: false
    },
    plugins: {
      title: {
        display: true,
        text: "Total Jumlah Corrective Maintenance",
        font: {
          size: 18,
          family: "Poppins, sans-serif",
          weight: "bold"
        },
        color: "#2c3e50"
      },
      tooltip: {
        enabled: true,
        backgroundColor: "#333",
        titleFont: { weight: "bold" },
        bodyFont: { size: 14 },
        padding: 10,
        cornerRadius: 5
      },
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
          color: "#34495e",
          font: { size: 12 },
          callback: value => Number.isInteger(value) ? value : null
        },
        grid: {
          color: "#ecf0f1"
        }
      },
      x: {
        ticks: {
          color: "#34495e",
          font: { size: 12 }
        },
        grid: {
          display: false
        }
      }
    }
  }
});


console.log(mostUseSparepart)


new Chart(sparepartChart, {
  type: "bar",
  data: {
    labels: sparepart,
    datasets: [{
      label: "Jumlah Sparepart",
      backgroundColor: colorStart,
      hoverBackgroundColor: "#1abc9c",
      borderRadius: 8,
      data: jumlahSparepart
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: 20
    },
    plugins: {
      title: {
        display: true,
        text: "Penggunaan Sparepart Tahun Ini",
        font: {
          size: 20,
          weight: "bold",
          family: "Poppins, sans-serif"
        },
        color: "#2c3e50",
        padding: {
          bottom: 20
        }
      },
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: "#2c3e50",
        titleFont: { size: 14, weight: "bold" },
        bodyFont: { size: 13 },
        padding: 10,
        cornerRadius: 6
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
          callback: value => Number.isInteger(value) ? value : null,
          color: "#34495e",
          font: { size: 12 }
        },
        grid: {
          color: "#ecf0f1"
        }
      },
      x: {
        ticks: {
          color: "#34495e",
          font: { size: 12 }
        },
        grid: {
          display: false
        }
      }
    },
    animation: {
      duration: 1000,
      easing: "easeOutBounce"
    },
    hover: {
      mode: "index",
      intersect: false
    }
  }
});




new Chart(machineChart, {
  type: "bar",
  data: {
    labels: mesin,
    datasets: [{
      label: "Jumlah Kerusakan",
      data: jumlahMesin,
      backgroundColor: colorStart,
      hoverBackgroundColor: "#1abc9c",
      borderRadius: 8,
      barPercentage: 0.6,
      categoryPercentage: 0.8
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: 10
    },
    plugins: {
      title: {
        display: true,
        text: "Kerusakan Mesin Bulan Ini",
        font: {
          size: 18,
          family: "Poppins, sans-serif",
          weight: "bold"
        },
        color: "#2c3e50"
      },
      tooltip: {
        enabled: true,
        backgroundColor: "#333",
        titleFont: { weight: "bold" },
        bodyFont: { size: 14 },
        padding: 10,
        cornerRadius: 5
      },
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
          color: "#34495e",
          font: { size: 12 },
          callback: value => Number.isInteger(value) ? value : null
        },
        grid: {
          color: "#ecf0f1"
        }
      },
      x: {
        ticks: {
          color: "#34495e",
          font: { size: 12 }
        },
        grid: {
          display: false
        }
      }
    }
  }
});
