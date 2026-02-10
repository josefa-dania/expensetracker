let expenses = [];
const budget = 30000;

let chart; // Chart.js instance

function addExpense() {
  const name = document.getElementById("expenseName").value;
  const amount = parseFloat(document.getElementById("expenseAmount").value);
  const category = document.getElementById("expenseCategory").value;

  if (!name || isNaN(amount)) {
    alert("Please fill out both name and amount!");
    return;
  }

  expenses.push({ name, amount, category });
  document.getElementById("expenseName").value = "";
  document.getElementById("expenseAmount").value = "";
  updateSummary();
}

function updateSummary() {
  const summary = {};
  let total = 0;

  for (const exp of expenses) {
    summary[exp.category] = (summary[exp.category] || 0) + exp.amount;
    total += exp.amount;
  }

  const remaining = budget - total;
  const today = new Date();
  const daysInMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();
  const remainingDays = daysInMonth - today.getDate();
  const daily = remainingDays > 0 ? remaining / remainingDays : 0;

  const summaryDiv = document.getElementById("expenseSummary");
  summaryDiv.innerHTML = "";
  for (const [category, amt] of Object.entries(summary)) {
    const p = document.createElement("p");
    p.textContent = `${category}: ₹${amt.toFixed(2)}`;
    summaryDiv.appendChild(p);
  }

  document.getElementById("totalSpent").textContent = `Total Spent: ₹${total.toFixed(2)}`;
  document.getElementById("remainingBudget").textContent = `Budget Remaining: ₹${remaining.toFixed(2)}`;
  document.getElementById("dailyBudget").textContent = ` Budget Per Day: ₹${daily.toFixed(2)}`;

  updateChart(summary);
}

function updateChart(summary) {
  const ctx = document.getElementById("expenseChart").getContext("2d");

  const data = {
    labels: Object.keys(summary),
    datasets: [{
      label: "Expenses",
      data: Object.values(summary),
      backgroundColor: [
        "#f87171", // red
        "#60a5fa", // blue
        "#34d399", // green
        "#fbbf24", // yellow
        "#a78bfa"  // purple
      ],
      borderColor: "#fff",
      borderWidth: 2,
    }]
  };

  const config = {
    type: "pie",
    data: data,
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "bottom"
        }
      }
    }
  };

  // Destroy old chart if it exists
  if (chart) {
    chart.destroy();
  }

  chart = new Chart(ctx, config);
}
