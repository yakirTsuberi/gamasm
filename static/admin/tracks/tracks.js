app.controller('TracksContainer', function ($scope, $http) {
    var vm = this;
    vm.companies = {
        cellcom: 'סלקום', partner: 'פרטנר', pelephon: 'פלאפון',
        '012': '012 מובייל', hot: 'הוט מובייל', golan: 'גולן טלקום', rami_levi: 'רמי לוי'
    };
    $http.get('/api/admin/tracks').then(
        function (response) {
            vm.tracks = response.data
        })
});

