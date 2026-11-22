from django import forms
from .models import Pago

class PagoAdminForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        venta = cleaned_data.get("venta")
        importe = cleaned_data.get("importe")

        if venta is not None and importe is not None:
            pagos_previos = venta.pagos.exclude(pk=self.instance.pk)
            total = sum((pago.importe for pago in pagos_previos), importe)
            if total > venta.monto_total:
                self.add_error(
                    "importe",
                    "El importe produciría un sobrepago: la suma de los pagos "
                    "no puede superar el monto total de la venta.",
                )

        return cleaned_data
