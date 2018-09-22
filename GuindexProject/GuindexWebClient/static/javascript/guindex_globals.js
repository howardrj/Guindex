var G_API_BASE = location.protocol + '//' + location.hostname + ':' + location.port + '/api/';

// Global variables to keep track of user state
// TODO Add these to object
var g_loggedIn            = false;
var g_accessToken         = null;
var g_userId              = null;
var g_username            = null;
var g_isStaffMember       = null;
var g_email               = null; 
var g_facebookAccessToken = null;
