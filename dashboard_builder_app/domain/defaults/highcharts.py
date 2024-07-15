


HIGHCHARTS_DEFAULTS = {
    "chart": {
        "type": "column"
    },
    "title": {
        "text": "Example Title"
    },
    "subtitle": {
        "text": "Source: <a href=\"https://multikrd.com\" target=\"_blank\">Multikrd</a>"
    },
    "xAxis": {
        "type": "category",
        "labels": {
            "autoRotation": [-45, -90],
            "style": {
                "fontSize": "13px",
                "fontFamily": "Verdana, sans-serif"
            }
        }
    },
    "yAxis": {
        "min": 0,
        "title": {
            "text": "Wage access (USD)"
        }
    },
    "legend": {
        "enabled": False
    },
    "tooltip": {
        "pointFormat": "Wage access in 2024: <b>{point.y:.1f}</b>"
    },
    "series": [{
        "name": "Wage access",
        "colorByPoint": True,
        "data": [
            ["insperity | Farm Fresh Rhode Island", 103.75],
            ["insperity | Sobrius Operations LLC", 189.00],
            ["insperity | Washington Ballet", 303.75],
            ["insperity | Morris Brown College", 393.75],
            ["insperity | Twin Cities Senior Care LLC", 520.75],
            ["insperity | Explorent LLC", 602.50],
            ["insperity | SoCal Empowered LLC", 647.00],
            ["insperity | H-I Electric Inc", 2011.25],
            ["insperity | Doors West, Inc", 2151.25],
            ["insperity | Guardian Medical Services Inc", 2916.00],
            ["insperity | Brookhaven Market", 3537.50],
            ["insperity | Nemalife, Inc", 6044.00],
            ["insperity | Brite Consulting LLC", 8194.50],
            ["insperity | Lowcountry Nursing Group LLC", 13127.50],
            ["kazpay | Tactical Overwatch Command LLC", 309.00],
            ["multikrd | Go Green Texas EV", 1981.50],
            ["multikrd | Graham County Rehabilitation Center", 4184.75],
            ["multikrd | Puff Group", 12668.75]
        ],
        "dataLabels": {
            "enabled": True,
            "rotation": -90,
            "color": "#FFFFFF",
            "inside": True,
            "verticalAlign": "top",
            "format": "{point.y:.1f}",
            "y": 10,
            "style": {
                "fontSize": "13px",
                "fontFamily": "Verdana, sans-serif"
            }
        }
    }]
}
