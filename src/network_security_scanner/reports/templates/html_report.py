"""HTML report template."""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Security Scan Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            margin: -30px -30px 30px -30px;
            border-radius: 8px 8px 0 0;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background-color: #ecf0f1; 
            padding: 20px; 
            border-radius: 6px; 
            text-align: center; 
        }
        .device { 
            margin: 20px 0; 
            padding: 20px; 
            border: 1px solid #ddd; 
            border-radius: 6px; 
        }
        .severity-critical { border-left: 5px solid #e74c3c; }
        .severity-high { border-left: 5px solid #f39c12; }
        .severity-medium { border-left: 5px solid #f1c40f; }
        .severity-low { border-left: 5px solid #27ae60; }
        .finding { 
            background-color: #f8f9fa; 
            margin: 10px 0; 
            padding: 15px; 
            border-radius: 4px; 
        }
        .badge { 
            display: inline-block; 
            padding: 4px 8px; 
            border-radius: 4px; 
            color: white; 
            font-size: 12px; 
            font-weight: bold; 
        }
        .badge-critical { background-color: #e74c3c; }
        .badge-high { background-color: #f39c12; }
        .badge-medium { background-color: #f1c40f; color: #333; }
        .badge-low { background-color: #27ae60; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Network Security Scan Report</h1>
            <p>Generated on {{ timestamp }}</p>
        </div>

        <div class="summary">
            <div class="summary-card">
                <h3>Total Devices</h3>
                <div style="font-size: 2em; font-weight: bold;">{{ total_devices }}</div>
            </div>
            <div class="summary-card">
                <h3>Total Findings</h3>
                <div style="font-size: 2em; font-weight: bold;">{{ total_findings }}</div>
            </div>
            <div class="summary-card">
                <h3>Critical Issues</h3>
                <div style="font-size: 2em; font-weight: bold; color: #e74c3c;">{{ critical_count }}</div>
            </div>
            <div class="summary-card">
                <h3>High Issues</h3>
                <div style="font-size: 2em; font-weight: bold; color: #f39c12;">{{ high_count }}</div>
            </div>
        </div>

        {% for device in devices %}
        <div class="device">
            <h2>{{ device.hostname }} ({{ device.device_type }})</h2>
            <p><strong>Configuration File:</strong> {{ device.config_file }}</p>

            {% for finding in device.findings %}
            <div class="finding severity-{{ finding.severity }}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4>{{ finding.title }}</h4>
                    <span class="badge badge-{{ finding.severity }}">{{ finding.severity.upper() }}</span>
                </div>
                <p>{{ finding.description }}</p>
                <small><strong>Category:</strong> {{ finding.category }}</small>
            </div>
            {% endfor %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""  # noqa: W291
