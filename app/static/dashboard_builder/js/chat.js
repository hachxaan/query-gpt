document.addEventListener("DOMContentLoaded", function() {
    $(document).ready(function() {
        $('#data-table').DataTable({
            "bInfo": true, 
            "paging": true, 
            "searching": true, 
            "ordering": true, 
            "order": [[0, 'asc']] 
        });
    });

    Highcharts.chart('cnt-chart', {
        chart: {
            type: 'column'
        },
        title: {
            text: 'Créditos otorgados en el último año agrupados por White Label'
        },
        xAxis: {
            categories: ['abacus', 'multikrdcsv', 'assethr', 'test', 'insperity', 'pasaporte-migrante', 'payplus', 'kazpay']
        },
        yAxis: {
            title: {
                text: 'Cantidad de Créditos'
            }
        },
        series: [{
            name: 'Recurrent Solid Credit',
            data: [30, 0, 56, 50, 92, 0, 0, 23]
        }, {
            name: 'Recurrent Tabapay Credit',
            data: [42, 0, 26, 0, 55, 50, 5, 30]
        }, {
            name: 'Regular ACH Credit',
            data: [11, 0, 8, 0, 31, 4, 0, 13]
        }, {
            name: 'Regular Solid Credit',
            data: [24, 0, 20, 16, 113, 13, 5, 24]
        }, {
            name: 'Regular Tabapay Credit',
            data: [10, 0, 11, 3, 36, 4, 5, 9]
        }]
    });

    let chatMessages = document.getElementById('cnt-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
});
