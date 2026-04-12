// Add-pub map: Leaflet + OpenStreetMap (no Google Maps API key).

var g_addPubMap = null;
var g_pubLocationMarker = null;

var G_ZOOM = 17;
// [lat, lng] for Leaflet
var G_DUBLIN_CENTER = [53.34528, -6.272161];

function createAddPubMap(center) {
    var container = document.getElementById("add_pub_map");
    if (!container || typeof L === "undefined") {
        return;
    }
    if (g_addPubMap) {
        g_addPubMap.remove();
        g_addPubMap = null;
        g_pubLocationMarker = null;
    }

    g_addPubMap = L.map(container, {
        zoomControl: true,
        scrollWheelZoom: true,
    }).setView(center, G_ZOOM);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
        // OSM expects a Referer (typically origin) on tile requests; do not use no-referrer
        referrerPolicy: "strict-origin-when-cross-origin",
    }).addTo(g_addPubMap);

    g_pubLocationMarker = L.marker(center, {
        draggable: true,
        title: "New Pub Location",
    }).addTo(g_addPubMap);

    g_addPubMap.on("click", function (evt) {
        g_pubLocationMarker.setLatLng(evt.latlng);
    });

    setTimeout(function () {
        if (g_addPubMap) {
            g_addPubMap.invalidateSize();
        }
    }, 100);
}

function initAddPubMap() {
    if (!document.getElementById("add_pub_map")) {
        return;
    }
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                createAddPubMap([
                    position.coords.latitude,
                    position.coords.longitude,
                ]);
            },
            function () {
                createAddPubMap(G_DUBLIN_CENTER);
            }
        );
    } else {
        createAddPubMap(G_DUBLIN_CENTER);
    }
}

function onDataAddPubTabDisplay() {
    var container = document.getElementById("add_pub_map");
    if (!container) {
        return;
    }
    if (!g_addPubMap) {
        initAddPubMap();
    } else {
        setTimeout(function () {
            if (g_addPubMap) {
                g_addPubMap.invalidateSize();
            }
        }, 100);
    }
}

$(document).on("click", "#add_pub_submit_button", function () {
    if (!g_loggedIn || !g_accessToken) {
        displayMessage("Error", "You must be logged in to add a pub.");
        return;
    }

    if (!g_pubLocationMarker) {
        displayMessage("Error", "Map is not ready yet. Please wait or refresh.");
        return;
    }

    var name = document.getElementById("add_pub_name").value;
    var countySelect = document.getElementById("add_pub_county");
    var county = countySelect ? countySelect.value.trim() : "";
    var ll = g_pubLocationMarker.getLatLng();

    var new_pub_data = {
        name: name,
        county: county,
        latitude: ll.lat,
        longitude: ll.lng,
    };

    var request = new XMLHttpRequest();

    request.open("POST", G_API_BASE + "pubs/", true);
    request.setRequestHeader("Content-Type", "application/json");
    request.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    request.setRequestHeader("Authorization", "Token " + g_accessToken);

    request.send(JSON.stringify(new_pub_data));

    var button = this;
    toggleLoader(button);

    request.onreadystatechange = function processRequest() {
        if (request.readyState === 4) {
            toggleLoader(button);

            var response;
            try {
                response = JSON.parse(request.responseText);
            } catch (e) {
                displayMessage(
                    "Error",
                    "Unexpected response from server (status " +
                        request.status +
                        ")."
                );
                return;
            }

            if (request.status === 201) {
                if (g_isStaffMember) {
                    displayMessage(
                        "Info",
                        "Thank you. Your submission was successful."
                    );
                } else {
                    displayMessage(
                        "Info",
                        "Thank you. A member of staff will verify your submission shortly."
                    );
                }
                document.getElementById("add_pub_name").value = "";
            } else {
                var error_message =
                    "<p>Please fix the following error(s): </p>";
                var error_table =
                    '<table border="1" cellpadding="5" style="margin: 5px auto"><tbody>';
                error_table +=
                    "<tr> <th> Field </th> <th> Error </th> </tr>";

                Object.keys(response).forEach(function (key) {
                    error_table += "<tr>";
                    error_table += "<td>" + key + "</td>";
                    error_table += "<td>" + response[key] + "</td>";
                    error_table += "</tr>";
                });

                error_table += "</tbody></table>";
                displayMessage("Error", error_message + error_table);
            }
        }
    };
});

(function bindAddPubTabDisplay() {
    var page = document.getElementById("data_add_pub_page");
    if (!page) {
        return;
    }
    page.addEventListener("tab_display", onDataAddPubTabDisplay);
})();
