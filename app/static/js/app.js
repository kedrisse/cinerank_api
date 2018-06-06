document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems, {});
    var tabs = document.querySelectorAll('.tabs');
    var instance = M.Tabs.init(tabs, {});
});