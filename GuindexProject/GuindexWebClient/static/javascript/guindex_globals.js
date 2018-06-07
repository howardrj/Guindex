// Useful global constants and variables
var G_API_BASE             = location.protocol + '//' + location.hostname + ':' + location.port + '/api/';
var G_FACEBOOK_APP_ID      = '{{facebook_app_id}}';
var G_GUI_REFRESH_INTERVAL = 300000;

// Global variables to keep track of user state
var g_loggedIn            = false;
var g_accessToken         = null;
var g_userId              = null;
var g_username            = null;
var g_isStaffMember       = null;
var g_email               = null; 
var g_facebookAccessToken = null;

// Global object lists
var g_pubsList                = [];
var g_contributorsList        = [];
var g_stats                   = {};
var g_detailedContributorInfo = {};

// Global DataTable objects
var g_guindexDataTable        = null;
var g_guindexStatsTable       = null;
var g_guindexPriceTable       = null;
var g_userContributionsTable  = null;
var g_userSettingsTable       = null;
var g_pendingPriceCreateTable = null;
var g_pendingPubCreateTable   = null;
var g_pendingPubPatchTable    = null;
