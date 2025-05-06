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

new Chart("woChart", {
  type: "bar",
  data: {
    labels: bulan,
    datasets: [{
      backgroundColor: "red",
      data: jumlahWo
    }]
  },
  options: {
    title: {
      display: true,
      text: "Jumlah WO Perbulan"
    }
  }
});

console.log(mostUseSparepart)
new Chart("sparepartChart",{
  type: "bar",
  data: {
    labels: sparepart,
    datasets: [{
      backgroundColor: "blue",
      data: jumlahSparepart
    }]
  },
  options: {
    title: {
      display: true,
      text: "Penggunaan Sparepart Tahun Ini"
    }
  }
});

new Chart("machineChart",{
  type: "bar",
  data:{
    labels: mesin,
    datasets: [{
      data:jumlahMesin,
      backgroundColor: "cyan"
    }]
  },
  options:{
    title: {
      display: true,
      text: "Kerusakan Mesin Bulan Ini"
    }
  }
});