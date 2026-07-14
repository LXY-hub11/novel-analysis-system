$(document).ready(function() {
    console.log('Novel Analysis System Loaded');

    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        var target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 70
            }, 500);
        }
    });

    $('.navbar-menu a').each(function() {
        if (window.location.pathname === $(this).attr('href')) {
            $(this).addClass('active');
        }
    });

    $('form').on('submit', function() {
        $(this).find('button[type="submit"]').prop('disabled', true).text('处理中...');
    });

    $('.star').hover(
        function() {
            $(this).prevAll().addBack().addClass('hover');
        },
        function() {
            $(this).prevAll().addBack().removeClass('hover');
        }
    );

    function showToast(message, type = 'info') {
        var toast = $('<div class="toast" style="position:fixed;bottom:20px;right:20px;padding:1rem 2rem;background:' +
            (type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3') +
            ';color:white;border-radius:8px;z-index:9999;box-shadow:0 2px 8px rgba(0,0,0,0.2);">' + message + '</div>');
        $('body').append(toast);
        setTimeout(function() {
            toast.fadeOut(function() { $(this).remove(); });
        }, 3000);
    }

    window.showToast = showToast;

    $(window).on('resize', function() {
        if (typeof chart !== 'undefined' && chart.resize) {
            chart.resize();
        }
    });

    $('img').on('error', function() {
        $(this).attr('src', 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23667eea" width="200" height="200"/%3E%3Ctext fill="white" font-size="20" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3ENo Image%3C/text%3E%3C/svg%3E');
    });
});
