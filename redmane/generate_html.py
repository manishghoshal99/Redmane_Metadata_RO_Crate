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
        body { font-family: "Segoe UI", "Roboto", "Helvetica Neue", sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; background: #fff; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-radius: 8px; }
        h1 { color: #2c3e50; font-weight: 300; margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 20px; }
        h2 { color: #34495e; font-weight: 500; font-size: 1.5em; margin-top: 30px; }
        
        .summary-box { background: #fff; padding: 20px; border-radius: 8px; border: 1px solid #eef2f5; margin-bottom: 30px; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .stat-item { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #e9ecef; }
        .stat-value { font-size: 28px; font-weight: 600; color: #3498db; margin-bottom: 5px; }
        .stat-label { color: #95a5a6; font-size: 13px; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }
        
        table { width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 15px; border: 1px solid #eef2f5; border-radius: 6px; overflow: hidden; }
        th, td { padding: 14px 18px; text-align: left; border-bottom: 1px solid #eef2f5; }
        th { background-color: #f8f9fa; font-weight: 600; color: #7f8c8d; font-size: 14px; text-transform: uppercase; }
        tr:last-child td { border-bottom: none; }
        tr:hover { background-color: #fcfcfc; }
        
        .upload-link { text-align: right; margin-bottom: 0; }
        .upload-btn { background: #27ae60; color: white; padding: 10px 24px; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 14px; transition: all 0.2s; box-shadow: 0 2px 4px rgba(39, 174, 96, 0.2); }
        .upload-btn:hover { background: #219150; box-shadow: 0 4px 8px rgba(39, 174, 96, 0.3); transform: translateY(-1px); }
        
        #error-message { background: #fff5f5; color: #e74c3c; padding: 20px; border-radius: 6px; border: 1px solid #ffebea; display: none; margin-bottom: 20px; }
        .loading { text-align: center; padding: 60px; color: #95a5a6; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <div id="error-message"></div>
        
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h1>Files Summary</h1>
            <!-- Placeholder for filtering/search -->
            <div style="margin: 0 20px; flex-grow: 1; max-width: 400px;">
                <input type="text" placeholder="Filter files (coming soon)..." disabled 
                       style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; background: #f9f9f9;">
            </div>
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
