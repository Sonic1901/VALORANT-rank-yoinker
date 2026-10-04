/*jshint esversion: 6 */

// Download Counter
fetch('https://api.github.com/repos/Sonic1901/VALORANT-rank-yoinker/releases')
    .then(response => response.json())
    .then(data => process_data(Array.isArray(data) ? data : []))
    .catch(error => console.warn('Unable to load release download count:', error));

function process_data(data) {
    console.log(data);
    let downloads_count = 0;
    for (let i = 0; i < data.length; i++) {
        const assets = Array.isArray(data[i].assets) ? data[i].assets : [];
        downloads_count += assets.reduce(
            (total, asset) => total + (Number(asset.download_count) || 0),
            0
        );
    }
    document.getElementById("downloads").innerHTML = "Total Downloads: " + downloads_count;
}
