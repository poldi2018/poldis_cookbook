queue()
            .defer(d3.json, "static/data/all_recipes.json")
            .await(makeGraphs);

        function makeGraphs(error, transactionsData) {
            var ndx = crossfilter(transactionsData);

            var user_dim = ndx.dimension(dc.pluck('added_by'));
            var total_viewcount_per_user = user_dim.group().reduceSum(dc.pluck('view_count'));
            dc.pieChart('#per-user-viewcount')
                .height(330)
                .radius(90)
                .transitionDuration(1500)
                .dimension(user_dim)
                .group(total_viewcount_per_user);

            var user_dim = ndx.dimension(dc.pluck('added_by'));
            var total_reviewcount_per_user = user_dim.group().reduceSum(dc.pluck('review_count'));
            dc.pieChart('#per-user-reviewcount')
                .height(330)
                .radius(90)
                .transitionDuration(1500)
                .dimension(user_dim)
                .group(total_reviewcount_per_user);

            dc.renderAll();
        }