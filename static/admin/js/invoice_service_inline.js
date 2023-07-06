function updatePrice(select) {
    var row = select.closest('.dynamic-invoiceservice_set');
    var quantityInput = row.querySelector('.field-quantity input');
    var priceField = row.querySelector('.field-service select option:checked');

    var quantity = parseInt(quantityInput.value) || 0;
    var priceString = priceField.textContent || '';
    var price = parseFloat(priceString.split(' - ')[1]) || 0;
    var totalPrice = quantity * price;

    row.querySelector('.field-total_price input').value = totalPrice.toFixed(2);

    // Обновление общей суммы в верхней части формы
    updateTotalAmount();
}

function updateTotalPrice(input) {
    var row = input.closest('.dynamic-invoiceservice_set');
    var quantity = parseInt(input.value) || 0;
    var priceString = row.querySelector('.field-service select option:checked').textContent || '';
    var price = parseFloat(priceString.split(' - ')[1]) || 0;
    var totalPrice = quantity * price;

    row.querySelector('.field-total_price input').value = totalPrice.toFixed(2);

    // Обновление общей суммы в верхней части формы
    updateTotalAmount();
}

function updateTotalAmount() {
    var totalAmount = 0;
    var rows = document.querySelectorAll('.dynamic-invoiceservice_set');

    rows.forEach(function (row) {
        var totalPriceString = row.querySelector('.field-total_price input').value || '';
        var totalPrice = parseFloat(totalPriceString.replace(',', '.')) || 0;
        totalAmount += totalPrice;
    });

    // Обновление поля total_amount в верхней части формы
    document.querySelector('#id_total_amount').value = totalAmount.toFixed(2);
}

document.addEventListener('DOMContentLoaded', function() {
    var totalAmountField = document.querySelector('#id_total_amount');
    totalAmountField.setAttribute('readonly', 'readonly');
});
