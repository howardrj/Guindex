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
var g_detailedContributorInfo = {};

// Global DataTable objects
var g_guindexStatsTable       = null;
var g_userContributionsTable  = null;
var g_userSettingsTable       = null;
var g_pendingPriceCreateTable = null;
var g_pendingPubCreateTable   = null;
var g_pendingPubPatchTable    = null;
