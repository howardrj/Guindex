Dashing.widgets.Prices = function(dashboard) {
    var self = this;
    self.__init__ = Dashing.utils.widgetInit(dashboard, 'prices');
    self.row = 1;
    self.col = 1;
    self.color = '#ff0000';
    self.scope = {};
    self.getWidget = function () {
        return this.__widget__;
    };
    self.getData = function () {};
    self.interval = 1000;
};
