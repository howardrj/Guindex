Dashing.widgets.LoginWithFacebook = function(dashboard) {
    var self = this;
    self.__init__ = Dashing.utils.widgetInit(dashboard, 'login_with_facebook');
    self.row = 1;
    self.col = 1;
    self.color = '#3B5998';
    self.scope = {};
    self.getWidget = function () {
        return this.__widget__;
    };
    self.getData = function () {};
    self.interval = 1000;
};
