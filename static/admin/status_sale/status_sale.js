app.controller('StatusSaleContainer', function ($scope, $http) {
    var vm = this;
    $http.get('/api/admin/transactions').then(
        function (response) {
            vm.status_sale = response.data
        })
});

