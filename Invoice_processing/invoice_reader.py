from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from config.config import endpoint, key
from datetime import date
import pandas as pd


document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

# def analyze_invoice(file_path):
#     path_to_sample_documents = file_path

#     with open(path_to_sample_documents, "rb") as f:
#         poller = document_analysis_client.begin_analyze_document(
#             "prebuilt-invoice", document=f, locale="en-US"
#         )
def analyze_invoice(blob_url):
    poller = document_analysis_client.begin_analyze_document_from_url(
        "prebuilt-invoice", document_url=blob_url, locale="en-US"
    )
    invoices = poller.result()
    data_list = []
    data = {}
    for idx, invoice in enumerate(invoices.documents):
        
        vendor_name = invoice.fields.get("VendorName")
        if vendor_name and vendor_name.value:
            data.update({"Vendor Name": {
                "value": vendor_name.value,
                "confidence": vendor_name.confidence
            }})
            data_list.append(["Vendor Name", vendor_name.value, vendor_name.confidence])

        vendor_address = invoice.fields.get("VendorAddress")
        if vendor_address and vendor_address.value:
            address_dict = vars(vendor_address.value)
            data.update({
                "Vendor Address": {
                    "value": address_dict,
                    "confidence": vendor_address.confidence
                }
            })
            data_list.append(["Vendor Address", address_dict, vendor_address.confidence])

        vendor_address_recipient = invoice.fields.get("VendorAddressRecipient")
        if vendor_address_recipient and vendor_address_recipient.value:
            data.update({"Vendor Address Recipient": {
                "value": vendor_address_recipient.value,
                "confidence": vendor_address_recipient.confidence
            }})
            data_list.append(["Vendor Address Recipient", vendor_address_recipient.value, vendor_address_recipient.confidence])

        customer_name = invoice.fields.get("CustomerName")
        if customer_name and customer_name.value:
            data.update({"Customer Name": {
                "value": customer_name.value,
                "confidence": customer_name.confidence
            }})
            data_list.append(["Customer Name", customer_name.value, customer_name.confidence])

        customer_id = invoice.fields.get("CustomerId")
        if customer_id and customer_id.value:
            data.update({"Customer Id": {
                "value": customer_id.value,
                "confidence": customer_id.confidence
            }})
            data_list.append(["Customer Id", customer_id.value, customer_id.confidence])

        customer_address = invoice.fields.get("CustomerAddress")
        if customer_address and customer_address.value:
            address_dict = vars(customer_address.value)
            data.update({"Customer Address": {
                "value": address_dict,
                "confidence": customer_address.confidence
            }})
            data_list.append(["Customer Address", address_dict, customer_address.confidence])

        customer_address_recipient = invoice.fields.get("CustomerAddressRecipient")
        if customer_address_recipient and customer_address_recipient.value:
            data.update({"Customer Address Recipient": {
                "value": customer_address_recipient.value,
                "confidence": customer_address_recipient.confidence
            }})
            data_list.append(["Customer Address Recipient", customer_address_recipient.value, customer_address_recipient.confidence])

        invoice_id = invoice.fields.get("InvoiceId")
        if invoice_id and invoice_id.value:
            data.update({"Invoice Id": {
                "value": invoice_id.value,
                "confidence": invoice_id.confidence
            }})
            data_list.append(["Invoice Id", invoice_id.value, invoice_id.confidence])

        invoice_date = invoice.fields.get("InvoiceDate")
        if invoice_date and invoice_date.value:
            date_value = invoice_date.value
            if isinstance(date_value, date):
                date_str = date_value.isoformat()
                data.update({"Invoice Date": {
                    "value": date_str,
                    "confidence": invoice_date.confidence
                }})
                data_list.append(["Invoice Date", date_str, invoice_date.confidence])

        invoice_total = invoice.fields.get("InvoiceTotal")
        if invoice_total and invoice_total.value:
            currency_dict = vars(invoice_total.value)
            data.update({"Invoice Total": {
                "value": currency_dict,
                "confidence": invoice_total.confidence
            }})
            data_list.append(["Invoice Total", currency_dict, invoice_total.confidence])

        due_date = invoice.fields.get("DueDate")
        if due_date and due_date.value:
            date_value = due_date.value
            if isinstance(date_value, date):
                date_str = date_value.isoformat()
                data.update({
                    "Due Date": {
                        "value": date_str,
                        "confidence": due_date.confidence
                    }
                })
                data_list.append(["Due Date", date_str, due_date.confidence])

        purchase_order = invoice.fields.get("PurchaseOrder")
        if purchase_order and purchase_order.value:
            data.update({"Purchase Order": {
                "value": purchase_order.value,
                "confidence": purchase_order.confidence
            }})
            data_list.append(["Purchase Order", purchase_order.value, purchase_order.confidence])

        billing_address = invoice.fields.get("BillingAddress")
        if billing_address and billing_address.value:
            address_dict = vars(billing_address.value)
            data.update({"Billing Address": {
                "value": address_dict,
                "confidence": billing_address.confidence
            }})
            data_list.append(["Billing Address", address_dict, billing_address.confidence])

        billing_address_recipient = invoice.fields.get("BillingAddressRecipient")
        if billing_address_recipient and billing_address_recipient.value:
            data.update({"Billing Address Recipient": {
                "value": billing_address_recipient.value,
                "confidence": billing_address_recipient.confidence
            }})
            data_list.append(["Billing Address Recipient", billing_address_recipient.value, billing_address_recipient.confidence])

        payment_details = invoice.fields.get("PaymentDetails")
        if payment_details:
            for detail in payment_details.value:
                iban = detail.value.get("IBAN")
                if iban and iban.value:
                    data.update({"Payment Details IBAN": {
                        "value": iban.value,
                        "confidence": iban.confidence
                    }})
                    data_list.append(["Payment Details IBAN", iban.value, iban.confidence])


                swift = detail.value.get("SWIFT")
                if swift and swift.value:
                    data.update({"Payment Details SWIFT": {
                        "value": swift.value,
                        "confidence": swift.confidence
                    }})
                    data_list.append(["Payment Details SWIFT", swift.value, swift.confidence])

                bank_account_number = detail.value.get("BankAccountNumber")
                if bank_account_number and bank_account_number.value:
                    data.update({"Payment Details Bank Account Number": {
                        "value": bank_account_number.value,
                        "confidence": bank_account_number.confidence
                    }})
                    data_list.append(["Payment Details Bank Account Number", bank_account_number.value, bank_account_number.confidence])

                bpay_biller_code = detail.value.get("BPayBillerCode")
                if bpay_biller_code and bpay_biller_code.value:
                    data.update({"Payment Details BPay Biller Code": {
                        "value": bpay_biller_code.value,
                        "confidence": bpay_biller_code.confidence
                    }})
                    data_list.append(["Payment Details BPay Biller Code", bpay_biller_code.value, bpay_biller_code.confidence])

                bpay_reference = detail.value.get("BPayReference")
                if bpay_reference and bpay_reference.value:
                    data.update({"Payment Details BPayReference": {
                        "value": bpay_reference.value,
                        "confidence": bpay_reference.confidence
                    }})
                    data_list.append(["Payment Details BPayReference", bpay_reference.value, bpay_reference.confidence])


        tax_details = invoice.fields.get("TaxDetails")
        if tax_details:
            for tax in tax_details.value:
                amount = tax.value.get("Amount")
                if amount and amount.value:
                    data.update({"Tax Details Amount": {
                        "value": {
                            "amount": amount.value.amount,
                            "symbol": amount.value.symbol,
                            "code": amount.value.code
                        },
                        "confidence": amount.confidence
                    }})
                    data_list.append(["Tax Details Amount", str(amount.value), amount.confidence])

                rate = tax.value.get("Rate")
                if rate and rate.value:
                    data.update({"Tax Details Rate": {
                        "value": rate.value,  # No need to convert to string if it's already in correct format
                        "confidence": rate.confidence
                    }})
                    data_list.append(["Tax Details Rate", rate.value, rate.confidence])



        installments = invoice.fields.get("PaidInFourInstallements")
        if installments:
            for installment in installments.value:
                amount = installment.value.get("Amount")
                if amount and amount.value:
                    data.update({"Paid in Four Installments Amount": {
                        "value": amount.value,
                        "confidence": amount.confidence
                    }})
                    data_list.append(["Paid in Four Installments Amount", amount.value, amount.confidence])


                # due_date = installment.value.get("DueDate")
                # if due_date and due_date.value:
                #     data.update({"Paid in Four Installments DueDate": {
                #         "value": due_date.value,
                #         "confidence": due_date.confidence
                #     }})

                due_date = installment.value.get("DueDate")
                if due_date and due_date.value:
                    date_value = due_date.value
                    if isinstance(date_value, date):
                        date_str = date_value.isoformat()
                        data.update({
                            "Paid in Four Installments DueDate": {
                                "value": date_str,
                                "confidence": due_date.confidence
                            }
                        })
                        data_list.append(["Paid in Four Installments DueDate", date_str, due_date.confidence])

        items = invoice.fields.get("Items")
        if items:
            for idx, item in enumerate(items.value):
                key = f"Invoice Item #{idx + 1}"
                if key not in data:
                    data[key] = {}

                data[key]['content'] = item.content
                data_list.append([f"{key} Content", item.content, None])

                # Handling Description
                item_description = item.value.get("Description")
                if item_description and item_description.value:
                    data[key].update({"Description": {
                        "value": item_description.value,
                        "confidence": item_description.confidence
                    }})
                    data_list.append([f"{key} Description", item_description.value, item_description.confidence])

                # Handling Quantity
                item_quantity = item.value.get("Quantity")
                if item_quantity and isinstance(item_quantity.value, (int, float)):
                    data[key].update({"Quantity": {
                        "value": item_quantity.value,
                        "confidence": item_quantity.confidence
                    }})
                    data_list.append([f"{key} Quantity", item_quantity.value, item_quantity.confidence])


                # Handling Unit
                unit = item.value.get("Unit")
                if unit and unit.value:
                    data[key].update({"Unit": {
                        "value": unit.value,
                        "confidence": unit.confidence
                    }})
                    data_list.append([f"{key} Unit", unit.value, unit.confidence])

                # Handling UnitPrice (Currency)
                unit_price = item.value.get("UnitPrice")
                if unit_price and unit_price.value:
                    currency_dict = vars(unit_price.value)  # Handling as a currency object
                    data[key].update({"Unit Price": {
                        "value": currency_dict,
                        "confidence": unit_price.confidence
                    }})
                    data_list.append([f"{key} Unit Price", currency_dict, unit_price.confidence])


                # Handling ProductCode
                product_code = item.value.get("ProductCode")
                if product_code and product_code.value:
                    data[key].update({"Product Code": {
                        "value": product_code.value,
                        "confidence": product_code.confidence
                    }})
                    data_list.append([f"{key} ProductCode", product_code.value, product_code.confidence])

                # Handling Date
                item_date = item.value.get("Date")
                if item_date and item_date.value:
                    date_value = item_date.value
                    if isinstance(date_value, date):
                        date_str = date_value.isoformat()
                        data[key].update({"Date": {
                            "value": date_str,
                            "confidence": item_date.confidence
                        }})
                        data_list.append([f"{key} Date", date_str, item_date.confidence])


                # Handling Tax (Currency)
                tax = item.value.get("Tax")
                if tax and tax.value:
                    currency_dict = vars(tax.value)  # Handling as a currency object
                    data[key].update({"Tax": {
                        "value": currency_dict,
                        "confidence": tax.confidence
                    }})
                    data_list.append([f"{key} Tax", currency_dict, tax.confidence])


                # Handling Amount (Currency)
                amount = item.value.get("Amount")
                if amount and amount.value:
                    currency_dict = vars(amount.value)  # Handling as a currency object
                    data[key].update({"Amount": {
                        "value": currency_dict,
                        "confidence": amount.confidence
                    }})
                    data_list.append([f"{key} Amount", currency_dict, amount.confidence])


        subtotal = invoice.fields.get("SubTotal")
        if subtotal and subtotal.value:
            currency_dict = vars(subtotal.value)
            data.update({"Subtotal": {
                "value": currency_dict,
                "confidence": subtotal.confidence
            }})
            data_list.append(["SubTotal", currency_dict, subtotal.confidence])

        total_tax = invoice.fields.get("TotalTax")
        if total_tax and total_tax.value:
            currency_dict = vars(total_tax.value)
            data.update({"Total Tax": {
                "value": currency_dict,
                "confidence": total_tax.confidence
            }})
            data_list.append(["TotalTax", currency_dict, total_tax.confidence])

        previous_unpaid_balance = invoice.fields.get("PreviousUnpaidBalance")
        if previous_unpaid_balance and previous_unpaid_balance.value:
            currency_dict = vars(previous_unpaid_balance.value)
            data.update({"Previous Unpaid Balance": {
                "value": currency_dict,
                "confidence": previous_unpaid_balance.confidence
            }})
            data_list.append(["Previous Unpaid Balance", currency_dict, previous_unpaid_balance.confidence])

        amount_due = invoice.fields.get("AmountDue")
        if amount_due and amount_due.value:
            currency_dict = vars(amount_due.value)
            data.update({"Amount Due": {
                "value": currency_dict,
                "confidence": amount_due.confidence
            }})
            data_list.append(["Amount Due", currency_dict, amount_due.confidence])


        service_start_date = invoice.fields.get("ServiceStartDate")
        if service_start_date and service_start_date.value:
            date_value = service_start_date.value
            if isinstance(date_value, date):
                date_str = date_value.isoformat()
                data.update({
                    "Service Start Date": {
                        "value": date_str,
                        "confidence": service_start_date.confidence
                    }
                })
                data_list.append(["Service Start Date", date_str, service_start_date.confidence])

        service_end_date = invoice.fields.get("ServiceEndDate")
        if service_end_date and service_end_date.value:
            date_value = service_end_date.value
            if isinstance(date_value, date):
                date_str = date_value.isoformat()
                data.update({
                    "Service End Date": {
                        "value": date_str,
                        "confidence": service_end_date.confidence
                    }
                })
                data_list.append(["Service End Date", date_str, service_start_date.confidence])
                



        service_address = invoice.fields.get("ServiceAddress")
        if service_address and service_address.value:
            address_dict = str(service_address.value)  # Convert to string
            data.update({"Service Address": {
                        "value":address_dict,
                        "confidence":service_address.confidence
                    }})
            data_list.append(["Service Address", address_dict, service_address.confidence])

        service_address_recipient = invoice.fields.get("ServiceAddressRecipient")
        if service_address_recipient and service_address_recipient.value:
            data.update({"Service Address Recipient": {
                        "value":service_address_recipient.value,
                        "confidence":service_address_recipient.confidence
                    }})
            data_list.append(["Service Address Recipient", service_address_recipient.value, service_address_recipient.confidence])
        remittance_address = invoice.fields.get("RemittanceAddress")
        if remittance_address and remittance_address.value:
            address_dict = str(remittance_address.value)  # Convert to string
            data.update({"Remittance Address": {
                        "value":address_dict,
                        "confidence":remittance_address.confidence
                    }})
            data_list.append(["Remittance Address", address_dict, remittance_address.confidence])

        remittance_address_recipient = invoice.fields.get("RemittanceAddressRecipient")
        if remittance_address_recipient and remittance_address_recipient.value:
            data.update({"Remittance Address Recipient": {
                        "value":remittance_address_recipient.value,
                        "confidence":remittance_address_recipient.confidence
                    }})
            data_list.append(["Remittance Address Recipient", remittance_address_recipient.value, remittance_address_recipient.confidence])
    # [END analyze_invoices]

        csv_path = "results1.csv"

   
        df = pd.DataFrame(data_list, columns=["Field", "Value", "Confidence"])
        df.to_csv(csv_path, mode='a', index=False)

        return data