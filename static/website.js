function itemurl(name, link) {
    Swal.fire({
        title: `${name}`,
        showCancelButton: true,
        cancelButtonText : 'ยกเลิก',
        confirmButtonText: 'ดู',
    }).then((result) => {
        if (result.isConfirmed) {
            window.location = `${link}`
        }
    })
}