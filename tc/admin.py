from django.contrib import admin
from import_export import resources
from import_export.admin import ExportActionModelAdmin
from tc.models import TrainingCourse
from BMS.admin_bms import BMS_admin_site
from django.contrib.auth.models import User
from django.db.models import Q


class TrainingCourseResource(resources.ModelResource):
    class Meta:
        model = TrainingCourse
        skip_unchanged = True
        fields = (
            "saler", "partner", "issuingUnit", "registration_fee", "content",
            "amount", "invoice_date", "amount_in", "amount_in_date",
            "trainingcourse", "note")
        export_order = (
            "saler", "partner", "issuingUnit", "registration_fee", "content",
            "amount", "invoice_date", "amount_in", "amount_in_date",
            "trainingcourse", "note")

    def get_export_headers(self):
        return ["销售", "客户", "开票单位", "报名费", "开票内容",
                "开票金额", "开票日期", "到款金额", "到款日期", "培训班", "备注"]


class TrainingCourseAdmin(ExportActionModelAdmin):
    model = TrainingCourse
    fields = ("saler", "partner", "issuingUnit", "registration_fee", "content",
              "amount", "invoice_date", "amount_in", "amount_in_date",
              "trainingcourse", "note", "is_submit")
    list_display = ("saler", "partner","issuingUnit", "registration_fee",
                    "trainingcourse", "is_submit")
    list_display_links = ("saler",)
    resource_class = TrainingCourseResource

    def get_readonly_fields(self, request, obj=None):
        try:
            if obj.is_submit:
                self.readonly_fields = ("saler", "partner", "issuingUnit",
                                        "registration_fee", "content",
                                        "amount", "invoice_date", "amount_in",
                                        "amount_in_date",
                                        "trainingcourse", "note", "is_submit")
                return self.readonly_fields
        except:
            return self.readonly_fields
        return self.readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "saler":
            saler_ = User.objects.filter(Q(groups__id=3) | Q(groups__id=6))
            kwargs["queryset"] = saler_
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


BMS_admin_site.register(TrainingCourse, TrainingCourseAdmin)
