document.addEventListener("DOMContentLoaded", function () {
    try {
        // ✅ Grab safe JSON from <script type="application/json">
        const salesChartLabels = JSON.parse(document.getElementById("chartLabels").textContent);
        const salesChartData = JSON.parse(document.getElementById("chartSales").textContent);

        let quoteChartData = null;
        const quoteEl = document.getElementById("chartQuotes");
        if (quoteEl) {
            quoteChartData = JSON.parse(quoteEl.textContent);
        }

        console.log("✅ Sales Chart Labels:", salesChartLabels);
        console.log("✅ Sales Chart Data:", salesChartData);
        if (quoteChartData) console.log("✅ Quote Chart Data:", quoteChartData);

        if (!salesChartLabels.length || !salesChartData.length) {
            console.warn("⚠️ No sales data available.");
            return;
        }

        const ctx = document.getElementById("salesChart");
        if (!ctx) {
            console.warn("⚠️ No canvas with ID 'salesChart' found.");
            return;
        }

        const datasets = [
            {
                label: "Monthly Sales ($)",
                data: salesChartData,
                backgroundColor: "rgba(75, 192, 192, 0.5)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 2,
                yAxisID: "y",
            }
        ];
        
        if (quoteChartData) {
            datasets.push({
                label: "Quote Requests",
                data: quoteChartData,
                backgroundColor: "rgba(255, 99, 132, 0.5)",
                borderColor: "rgba(255, 99, 132, 1)",
                borderWidth: 2,
                yAxisID: 'y1'  // ✅ Tell Chart.js to use right-side axis
            });
        }
        
        new Chart(ctx.getContext("2d"), {
            type: "bar",
            data: {
                labels: salesChartLabels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                if (context.dataset.label === "Monthly Sales ($)") {
                                    return `Sales: $${context.raw.toLocaleString()}`;
                                } else {
                                    return `Quote Requests: ${context.raw}`;
                                }
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45,
                        }
                    },
                    y: {
                        beginAtZero: true,
                        suggestedMax: Math.max(...salesChartData.concat(quoteChartData || [])) * 1.2,
                        title: {
                            display: true,
                            text: "Sales ($)"
                        }
                    },
                    y1: {
                        beginAtZero: true,
                        position: 'right',
                        grid: {
                            drawOnChartArea: false,
                        },
                        title: {
                            display: true,
                            text: "Quote Requests"
                        }
                    }
                }
            }
        });
    } catch (e) {
        console.error("❌ Chart render error:", e);
    }
});
