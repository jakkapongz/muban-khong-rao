function updateData(elementName, fieldName, referenceId) {

    const title = $('#row_' + fieldName + '_name_' + referenceId).text()

    console.log(title)

    $('#update' + elementName + 'Id').val(referenceId)
    $('#update' + elementName + 'Title').val(title)
    $('#update' + elementName + 'Modal').modal('show');
}

function showImage(title, base64Image) {
    $('#imagePreview').val(title)
    $('#imagePreview').attr('src', base64Image)
}

(function ($) {
    "use strict"; // Start of use strict

    $('#btnUpdateVisitor').click(function () {
        const visitor = {
            'visitor_id': $('#updateVisitorId').val(),
            'visitor_status': $('#updateVisitorStatus').val(),
            'visitor_remark': $('#updateVisitorReason').val()
        };

        $.ajax({
            type: "PUT",
            url: "/api/visitor",
            data: visitor,
            dataType: "json",
        }).done(function (data) {
            alert('บันทึกสำเร็จ')
            $('#updateVisitorModal').modal('hide');
            location.reload();
        }).fail(function (data) {
            alert('เกิดข้อผิดพลาด')
        });
    });

    $('#btnUpdateProblem').click(function () {

        const problem = {
            'problem_report_id': $('#updateProblemId').val(),
            'problem_report_status': $('#updateProblemStatus').val(),
            'problem_report_remark': $('#updateProblemReason').val()
        };

        $.ajax({
            type: "PUT",
            url: "/api/problem-report",
            data: problem,
            dataType: "json",
        }).done(function (data) {
            alert('บันทึกสำเร็จ')
            $('#updateProblemModal').modal('hide');
            location.reload();
        }).fail(function (data) {
            alert('เกิดข้อผิดพลาด')
        });

    });

    $('#visitorDataTable').DataTable({
        responsive: true,
        searching: false
    });

    $('#problemReportDataTable').DataTable({
        responsive: true,
        searching: false
    });

    $('#patrollingReportDataTable').DataTable({
        responsive: true,
        searching: false
    });

    $('#btnLogout').click(function () {
        $.ajax({
            type: "DELETE",
            url: "/api/logout",
            dataType: "json",
        }).done(function (data) {
            window.location.href = '/login'
        }).fail(function (data) {
            alert('เกิดข้อผิดพลาด')
        });
    })


})(jQuery); // End of use strict