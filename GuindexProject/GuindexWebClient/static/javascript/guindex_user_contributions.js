var g_userContributions = null;
var g_userContributionsTable = null;
var g_retrievingUserContributions = false;
var g_userContributionsTableRendered = false;

function escapeHtml(s) {
    if (s === null || s === undefined) {
        return '';
    }
    return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

/** Overall trophy from original price submission count (originalPrices). */
function originalbadges(A) {
    A = parseInt(A, 10);
    if (isNaN(A)) {
        A = 0;
    }
    var url = G_URL_BASE + '/static/images/';
    if (A < 0.5) {
        url += 'Trophy0.jpeg';
    } else if (A < 4.5) {
        url += 'Trophy1.jpeg';
    } else if (A < 9.5) {
        url += 'Trophy5.jpeg';
    } else if (A < 24.5) {
        url += 'Trophy10.jpeg';
    } else if (A < 49.5) {
        url += 'Trophy25.jpeg';
    } else if (A < 99.5) {
        url += 'Trophy50.jpeg';
    } else {
        url += 'Trophy100.jpeg';
    }
    return (
        '<img src="' +
        escapeHtml(url) +
        '" alt="Overall badge" title="Original prices submitted: ' +
        A +
        '" onerror="this.style.display=\'none\'" ' +
        'style="height:48px;width:auto;margin:4px;vertical-align:middle;" />'
    );
}

/** County badges: higher unique pub count first, then county name A-Z. */
function sortCountyBadges(badges) {
    if (!badges || !badges.length) {
        return [];
    }
    return badges.slice().sort(function (a, b) {
        var diff = (b.uniquePubs || 0) - (a.uniquePubs || 0);
        if (diff !== 0) {
            return diff;
        }
        return String(a.county).localeCompare(String(b.county));
    });
}

/** Renders county badge images (caller passes pre-sorted list). */
function renderCountyBadgesHtml(badges) {
    if (!badges || !badges.length) {
        return '';
    }
    var html = '';
    var i;
    for (i = 0; i < badges.length; i++) {
        var b = badges[i];
        var src = G_URL_BASE + '/static/images/' + b.image;
        var title =
            escapeHtml(b.county) +
            ': ' +
            b.uniquePubs +
            ' distinct pub' +
            (b.uniquePubs === 1 ? '' : 's') +
            ' · tier ' +
            b.tier;
        html +=
            '<img src="' +
            escapeHtml(src) +
            '" alt="' +
            escapeHtml(b.county) +
            ' (' +
            b.tier +
            ')" title="' +
            title +
            '" onerror="this.style.display=\'none\'" ' +
            'style="height:48px;width:auto;margin:4px;vertical-align:middle;" />';
    }
    return html;
}

/** Overall trophy first, then county badges (sorted by unique pubs desc, then county). */
function renderBadgesCell(originalPrices, countyBadges) {
    var overall = originalbadges(originalPrices);
    var sorted = sortCountyBadges(countyBadges || []);
    var countyHtml = renderCountyBadgesHtml(sorted);
    if (!countyHtml) {
        return overall;
    }
    return (
        '<span class="guindex-badge-overall">' +
        overall +
        '</span><span class="guindex-badge-counties" style="margin-left:8px;">' +
        countyHtml +
        '</span>'
    );
}

// Can only be called if user is logged in
function populateUserContributionsTable() {
    if (g_loggedIn) {
        var contributions_page = document.getElementById('contributions_page');

        contributions_page.getElementsByClassName('on_logged_in')[0].style.display =
            'block';
        contributions_page.getElementsByClassName('on_logged_out')[0].style.display =
            'none';
    } else {
        return;
    }

    if (g_userContributionsTableRendered) return;

    function getUserContributions(callback) {
        if (g_retrievingUserContributions) return;

        g_userContributions = null;

        // Function to get detailed info about this user using REST API
        var request = new XMLHttpRequest();

        request.open(
            'GET',
            G_API_BASE + 'contributors/' + g_userId + '/',
            true
        );

        request.setRequestHeader('Content-Type', 'application/json');
        request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        request.setRequestHeader('Authorization', 'Token ' + g_accessToken);

        request.send(null);

        g_retrievingUserContributions = true;

        request.onreadystatechange = function processRequest() {
            if (request.readyState == 4 && request.status == 200) {
                g_userContributions = JSON.parse(request.responseText);
                g_retrievingUserContributions = false;

                if (callback) callback();
            }
        };
    }

    if (g_userContributions == null) {
        getUserContributions(populateUserContributionsTable);
        return;
    }

    var table_data = [];

    table_data.push(['Pubs Visited', g_userContributions['pubsVisited']]);
    table_data.push([
        'Current Verifications',
        g_userContributions['currentVerifications'],
    ]);
    table_data.push(['Original Prices', g_userContributions['originalPrices']]);
    table_data.push([
        'Badges',
        renderBadgesCell(
            g_userContributions['originalPrices'],
            g_userContributions['countyBadges']
        ),
    ]);

    // Check if table is being drawn from scratch or refreshed
    if (!g_userContributionsTable) {
        data_columns = [
            { title: 'Statistic', orderable: false },
            { title: 'Value', orderable: false },
        ];

        g_userContributionsTable = $('#GuindexContributionsTable').DataTable({
            responsive: true,
            data: table_data,
            columns: data_columns,
            paging: false,
            ordering: false,
            searching: false,
        });
    } else {
        // Redraw table
        // TODO Stay on same page table
        g_userContributionsTable.clear().draw();
        g_userContributionsTable.rows.add(table_data);
        g_userContributionsTable.columns.adjust().draw();
    }

    g_userContributionsTableRendered = true;
}
