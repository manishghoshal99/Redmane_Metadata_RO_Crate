import json
from pathlib import Path
from html import escape
from .params import ORGANIZATION

# The template now includes Client-side JS to fetch and render data
# We use __JSON_FILENAME__ as a placeholder to avoid conflicts with JS template literals ${...}
DYNAMIC_VIEWER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>REDMANE Data Summary</title>
    <link rel='stylesheet' href='output.css'>
    <style>
        body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; color: #333; margin: 20px; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1, h2 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .summary-box { background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #e9ecef; margin-bottom: 30px; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .stat-item { background: white; padding: 15px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: center; }
        .stat-value { font-size: 24px; font-weight: bold; color: #3498db; }
        .stat-label { color: #7f8c8d; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 15px; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }
        th { background-color: #f8f9fa; font-weight: 600; color: #2c3e50; }
        tr:hover { background-color: #f1f1f1; }
        
        .upload-link { text-align: right; margin-bottom: 20px; }
        .upload-btn { background: #27ae60; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; transition: background 0.3s; }
        .upload-btn:hover { background: #219150; }
        
        #error-message { background: #fee; color: #c0392b; padding: 15px; border-radius: 5px; border: 1px solid #fcc; display: none; margin-bottom: 20px; }
        .loading { text-align: center; padding: 50px; color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="container">
        <div id="error-message"></div>
        
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h1>Files Summary</h1>
            <div class="upload-link">
                <a href="https://data-registry.example.org/upload" class="upload-btn">Upload Metadata</a>
            </div>
        </div>

        <div id="content">
            <div class="loading">Loading metadata from <code>__JSON_FILENAME__</code>...</div>
        </div>
    </div>

    <script>
        const JSON_FILE = "__JSON_FILENAME__";

        async function loadMetadata() {
            try {
                const response = await fetch(JSON_FILE);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                renderReport(data);
            } catch (e) {
                showError(`Failed to load metadata: ${e.message}<br><br>
                <strong>Note:</strong> If you are opening this file locally, modern browsers block reading Fetch API from file:// protocol.<br>
                Please use a local server: <code>python3 -m http.server</code> and open <a href="http://localhost:8000/__HTML_FILENAME__">http://localhost:8000/__HTML_FILENAME__</a>`);
            }
        }

        function renderReport(fullData) {
            const data = fullData.data;
            const files = data.files;
            
            // Calculate stats
            let totalFiles = 0;
            let totalSize = 0;
            const patients = new Set();
            const samples = new Set();
            const sizesByCat = {};

            for (const [cat, fileList] of Object.entries(files)) {
                let catSize = 0;
                totalFiles += fileList.length;
                
                for (const f of fileList) {
                    catSize += f.file_size;
                    
                    // Patient IDs
                    const pids = Array.isArray(f.patient_id) ? f.patient_id : [f.patient_id];
                    pids.forEach(p => { if(p) patients.add(p); });
                    
                    // Sample IDs
                    const sids = Array.isArray(f.sample_id) ? f.sample_id : [f.sample_id];
                    sids.forEach(s => { if(s) samples.add(s); });
                }
                sizesByCat[cat] = catSize;
                totalSize += catSize;
            }

            const html = `
                <p><strong>Location:</strong> ${data.location}</p>
                
                <div class="summary-box">
                    <h2>Summary Statistics</h2>
                    <div class="summary-grid">
                        <div class="stat-item">
                            <div class="stat-value">${totalFiles}</div>
                            <div class="stat-label">Total Files</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${patients.size}</div>
                            <div class="stat-label">Total Patients</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${samples.size}</div>
                            <div class="stat-label">Total Samples</div>
                        </div>
                         <div class="stat-item">
                            <div class="stat-value">${totalSize.toLocaleString()} ${data.file_size_unit}</div>
                            <div class="stat-label">Total Size</div>
                        </div>
                    </div>
                </div>

                ${renderTables(files)}
            `;
            
            document.getElementById('content').innerHTML = html;
        }

        function renderTables(filesMap) {
            const categories = ['raw', 'processed', 'summarised'];
            // add any others found
            Object.keys(filesMap).forEach(k => {
                if(!categories.includes(k)) categories.push(k);
            });

            let tablesHtml = '';
            
            for (const cat of categories) {
                if (!filesMap[cat] || filesMap[cat].length === 0) continue;
                
                const rows = filesMap[cat].map(f => {
                    // Truncate sample IDs for display
                    let sDisplay = Array.isArray(f.sample_id) ? f.sample_id : [f.sample_id];
                    if (sDisplay.length > 5) {
                        sDisplay = sDisplay.slice(0, 5).join(', ') + `... (${sDisplay.length})`;
                    } else {
                        sDisplay = sDisplay.join(', ');
                    }

                    // Format patient IDs
                    let pDisplay = Array.isArray(f.patient_id) ? f.patient_id.join(', ') : f.patient_id || '';

                    return `<tr>
                        <td>${f.file_name}</td>
                        <td>${f.file_size}</td>
                        <td>${pDisplay}</td>
                        <td>${sDisplay}</td>
                        <td>${f.directory}</td>
                    </tr>`;
                }).join('');

                tablesHtml += `
                    <h2>${cat.charAt(0).toUpperCase() + cat.slice(1)} Files</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>File Name</th>
                                <th>Size (KB)</th>
                                <th>Patient ID</th>
                                <th>Sample ID</th>
                                <th>Path</th>
                            </tr>
                        </thead>
                        <tbody>${rows}</tbody>
                    </table>
                `;
            }
            return tablesHtml;
        }

        function showError(msg) {
            const el = document.getElementById('error-message');
            el.innerHTML = msg;
            el.style.display = 'block';
            document.querySelector('.loading').style.display = 'none';
        }

        // Start loading
        loadMetadata();
    </script>
</body>
</html>
"""

def generate_html_from_json(json_path, html_path):
    """
    Generates a static HTML viewer that dynamically loads the JSON content.
    The html_path and json_path are assumed to be accessible relative to each other.
    """
    json_filename = Path(json_path).name
    html_filename = Path(html_path).name
    
    html = DYNAMIC_VIEWER_TEMPLATE.replace("__JSON_FILENAME__", json_filename)
    html = html.replace("__HTML_FILENAME__", html_filename)
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"HTML report viewer generated at: {html_path}")
    print(f"NOTE: To view {html_filename} correctly, you must serve it via HTTP (e.g., 'python -m http.server') or allow local file access in your browser.")
