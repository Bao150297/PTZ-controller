$(document).ready(() => {
    var player = videojs('player', {width: 350, height: 200})
    player.play()

    // Event handle for select tag
    // Iterate over each select element
    $('select').each(function () {
        // Cache the number of options
        var $this = $(this),
            numberOfOptions = $(this).children('option').length

        // Hides the select element
        $this.addClass('s-hidden')

        // Wrap the select element in a div
        $this.wrap('<div class="select"></div>')

        // Insert a styled div to sit over the top of the hidden select element
        $this.after('<div class="styledSelect"></div>')

        // Cache the styled div
        var $styledSelect = $this.next('div.styledSelect')

        // Show the first select option in the styled div
        $styledSelect.text($this.children('option').eq(0).text())

        // Insert an unordered list after the styled div and also cache the list
        var $list = $('<ul />', {
            'class': 'options'
        }).insertAfter($styledSelect)

        // Insert a list item into the unordered list for each select option
        for (var i = 0; i < numberOfOptions; i++) {
            $('<li />', {
                text: $this.children('option').eq(i).text(),
                rel: $this.children('option').eq(i).val()
            }).appendTo($list)
        }

        // Cache the list items
        var $listItems = $list.children('li')

        // Show the unordered list when the styled div is clicked (also hides it if the div is clicked again)
        $styledSelect.click(function (e) {
            e.stopPropagation()
            $('div.styledSelect.active').each(function () {
                $(this).removeClass('active').next('ul.options').hide()
            })
            $(this).toggleClass('active').next('ul.options').toggle()
        })

        // Hides the unordered list when a list item is clicked and updates the styled div to show the selected list item
        // Updates the select element to have the value of the equivalent option
        $listItems.click(function (e) {
            e.stopPropagation()
            $styledSelect.text($(this).text()).removeClass('active')
            $this.val($(this).attr('rel'))
            $list.hide()
            // alert($this.val())
            // Display moving style div according to user's selection
            if($this.attr("name")=="select_move"){
                var selected_move = $this.val()
                $(".move-div").each((index, ele) => {
                    $(ele).removeClass("d-block")
                    $(ele).addClass("d-none")
                    if($(ele).data("move") == selected_move)
                        $(ele).addClass("d-block")
                })
            }
        })

        // Hides the unordered list when clicking outside of it
        $(document).click(function () {
            $styledSelect.removeClass('active')
            $list.hide()
        })

    })

    // Request cotinouse move
    $(".direct").each((index, ele) => {
        $(ele).off().on("click", (e) => {
            var direction = $(ele).data("name")
            axios.post(`/direct?d=${direction}&t=con`)
        })
    })
    // Request absolute move
    $("#do_abs_move").off().on("click", () => {
        var abs_pan  = $("input[name='abs_pan']").val()
        var abs_tilt = $("input[name='abs_tilt']").val()
        var abs_zoom = $("input[name='abs_zoom']").val()
        axios.post(`/direct?t=abs`,
            data={pan: abs_pan, tilt: abs_tilt, zoom: abs_zoom},
            {headers:
                {'Content-Type': 'application/json'}
            })
    })
    // Request relative move
    $("#do_rel_move").off().on("click", () => {
        var rel_pan  = $("input[name='rel_pan']").val()
        var rel_tilt = $("input[name='rel_tilt']").val()
        var rel_zoom = $("input[name='rel_zoom']").val()
        axios.post(`/direct?t=rel`,
            data={pan: rel_pan, tilt: rel_tilt, zoom: rel_zoom},
            {headers:
                {'Content-Type': 'application/json'}
            })
    })

    // Re-useable sweet alert boxes
    function showLoading(title, timer=3600000, callback=null) {
        var toastMixin = Swal.mixin({
            toast: true,
            title: title,
            animation: true,
            position: 'top',
            showConfirmButton: false,
            allowEscapeKey: false,
            timer: timer,
            progressSteps: true,
            onOpen: () => {
                Swal.showLoading()
            },
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer)
                toast.addEventListener('mouseleave', Swal.resumeTimer)
            }
        })
        toastMixin.fire({
            animation: true,
        }).then(
           () => {
                if(callback)
                    callback(arguments[3])
           },
           (dismiss) => {}
        )
    }

    // Init canvas for point-click-move function
    var ctx = null
    var canvas = document.getElementById("point-loc")
    function init(){
        canvas.setAttribute('style', `width: 100%; height: 100%; position: absolute; top: 0; left: 0; z-index: 2;`)
        if(typeof G_vmlCanvasManager != 'undefined') {
            canvas = G_vmlCanvasManager.initElement(canvas)
        }
        ctx = canvas.getContext("2d")
        showLoading("Getting ready...", 600)
        setTimeout(()=>{
            canvas.setAttribute('width', $("#vid-container").offsetWidth)
            canvas.setAttribute('height', $("#vid-container").offsetHeight)
        }, 600)
    }

    init()

    // Get location when click on canvas
    var guessX = 0; //stores user's click on canvas
    var guessY = 0; //stores user's click on canvas
    function point_loc(event) {
        var x = event.offsetX
        var y = event.offsetY
        guessX = x
        guessY = y
        var scale_x = 640 / canvas.width
        var scale_y = 360 / canvas.height

        x /= scale_x
        y /= scale_y

        console.log('x', x, 'y', y)

        axios.post(`/direct?t=rel_c`,
            data = {x: x, y: y},
            {headers:
                {'Content-Type': 'application/json'}
            })
    }

    canvas.addEventListener("click", point_loc)

    function get_point_loc(canvas, event) {
        var x, y

        canoffset = $(canvas).offset()
        x = event.clientX + document.body.scrollLeft + document.documentElement.scrollLeft - Math.floor(canoffset.left)
        y = event.clientY + document.body.scrollTop + document.documentElement.scrollTop - Math.floor(canoffset.top) + 1

        return [x,y];
    }

})
