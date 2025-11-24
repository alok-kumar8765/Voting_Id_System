from django.contrib import admin
from .models import (Voter, State, Constituency, Booth,  AdminLog,
                    Address, BiometricData, FamilyRelation, DeathRecord, 
                    Notification, UpdateLog, DuplicateCheckLog, Localization,
                    TempVoter, Localization, LoginLog, BlacklistedVoter, MigrationHistory)
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.contrib.admin import SimpleListFilter
from datetime import date

# State AdminPanne;

class StateResource(resources.ModelResource):

    class Meta:
        model = State
        fields = ("id","name")
        
class StateResourceAdmin(ImportExportModelAdmin):
    resource_class = StateResource
    list_display = ("id","name")
    search_fields = ("id","name")
    ordering = ('name', 'id') 
    
admin.site.register(State, StateResourceAdmin)
  
# Constituency AdminPannel  
class ConstituencyResource(resources.ModelResource):

    class Meta:
        model = Constituency
        fields = ("id","name")
        
class ConstituencyResourceAdmin(ImportExportModelAdmin):
    resource_class = ConstituencyResource
    list_display = ("id","name")
    search_fields = ("id","name")
    ordering = ('name', 'id')
    
admin.site.register(Constituency, ConstituencyResourceAdmin)
       
# Booth AdminPannel
class BoothResource(resources.ModelResource):
    
    class Meta:
        model = Booth

class BoothResourceAdmin(ImportExportModelAdmin):
    resource_class = BoothResource
    list_display = ("id", "name", "constituency",)
    search_fields = ("id", "name", "constituency")
    ordering = ('name', 'id','constituency',) 
    
admin.site.register(Booth, BoothResourceAdmin)
        
# Admin AdminPannel
class AdminResource(resources.ModelResource):
    
    class Meta:
        model = AdminLog
        
class AdminLogAdmin(ImportExportModelAdmin): 
    resource_class = AdminResource
    list_display = ('id','admin','action','timestamp')
    ordering = ('admin', 'id','action','-timestamp') 
    
admin.site.register(AdminLog, AdminLogAdmin)

#=============================================
#Display Voter's Age 
#=============================================

class AgeYearFilter(SimpleListFilter):
    title = 'Age as of Year'          # Filter title in the sidebar
    parameter_name = 'year'           # Query parameter in the URL

    def lookups(self, request, model_admin):
        current_year = date.today().year
        # Last 10 years
        return [(str(y), str(y)) for y in range(current_year, current_year-10, -1)]

    def queryset(self, request, queryset):
        if self.value():
            year = int(self.value())
            # Example: filter voters born on or before target year
            # This is just a sample; adjust logic as needed
            return queryset.filter(dob__year__lte=year)
        return queryset
        
# Voter AdminPannel
class VoterResource(resources.ModelResource):
    
    class Meta:
        model = Voter
        exclude = ('photo_url','signature_url',)  # skip file fields


class VoterAdmin(ImportExportModelAdmin):
    resource_class = VoterResource
    
    # These must be here, inside the Admin class
    list_display = ('id', 'name',"get_age_current_year", 'phone', 'epic_number', 'status')
    search_fields = ('name', 'phone', 'epic_number')
    ordering = ('name', 'id','status','created_at')  
    list_filter = ('status','created_at','gender',AgeYearFilter)
    list_editable = ('status',)
    
    def get_age_current_year(self, obj):
        return obj.age_on_year()  # default: current year
    get_age_current_year.short_description = "Age"
    
admin.site.register(Voter, VoterAdmin)

#==========================================
 # Extented Tables
#==========================================

# Address AdminPannel
class AddressResource(resources.ModelResource):
    
    class Meta:
        model = Address
        
class AddressAdmin(ImportExportModelAdmin):
    resource_class = AddressResource
    
    # These must be here, inside the Admin class
    list_display = ('id', 'voter_id',"type", 'created_at', )
    search_fields = ('id', 'voter_id',)
    ordering = ( 'id','created_at')  
    list_editable = ('type',)
      
admin.site.register(Address, AddressAdmin)


# BiometricData AdminPannel
class BiometricDataResource(resources.ModelResource):
    
    class Meta:
        model = BiometricData
        
class BiometricDataAdmin(ImportExportModelAdmin):
    resource_class = BiometricDataResource
    
    # These must be here, inside the Admin class
    list_display = ('biometric_id', 'voter_id', 'created_at', )
    search_fields = ('biometric_id', 'voter_id',)
      
admin.site.register(BiometricData, BiometricDataAdmin)


# FamilyRelation AdminPannel
class FamilyRelationResource(resources.ModelResource):
    
    class Meta:
        model = FamilyRelation
        
class FamilyRelationAdmin(ImportExportModelAdmin):
    resource_class = FamilyRelationResource
    
    # These must be here, inside the Admin class
    list_display = ('relation_id', 'voter','relation_type','relative_name', 'created_at', )
    search_fields = ('relation_id', 'voter',)
      
admin.site.register(FamilyRelation, FamilyRelationAdmin)


# DeathRecord AdminPannel
class DeathRecordResource(resources.ModelResource):
    
    class Meta:
        model = DeathRecord
        
class DeathRecordAdmin(ImportExportModelAdmin):
    resource_class = DeathRecordResource
    
    # These must be here, inside the Admin class
    list_display = ('death_id', 'voter','verified_by_admin', )
    search_fields = ('death_id', 'voter',)
    #ordering = ( 'id','-verified_by_admin')  
    #list_editable = ('verified_by_admin',)
      
admin.site.register(DeathRecord, DeathRecordAdmin)

# Notification AdminPannel
class NotificationResource(resources.ModelResource):
    
    class Meta:
        model = Notification
        
class NotificationAdmin(ImportExportModelAdmin):
    resource_class = NotificationResource
    
    # These must be here, inside the Admin class
    list_display = ('notification_id', 'voter','notification_type', )
    search_fields = ('notification_id', 'voter',)
      
admin.site.register(Notification, NotificationAdmin)

# UpdateLog AdminPannel
class UpdateLogResource(resources.ModelResource):
    
    class Meta:
        model = UpdateLog
        
class UpdateLogAdmin(ImportExportModelAdmin):
    resource_class = UpdateLogResource
    
    # These must be here, inside the Admin class
    list_display = ('update_id', 'voter','updated_by_admin', )
    search_fields = ('update_id', 'voter',)
      
admin.site.register(UpdateLog, UpdateLogAdmin)

# DuplicateCheckLog AdminPannel
class DuplicateCheckLogResource(resources.ModelResource):
    
    class Meta:
        model = DuplicateCheckLog
        
class DuplicateCheckLogAdmin(ImportExportModelAdmin):
    resource_class = DuplicateCheckLogResource
    
    # These must be here, inside the Admin class
    list_display = ('check_id', 'voter','duplicate_found','check_date', )
    search_fields = ('check_id', 'voter','duplicate_found',)
      
admin.site.register(DuplicateCheckLog, DuplicateCheckLogAdmin)


# Localization AdminPannel
class LocalizationResource(resources.ModelResource):
    
    class Meta:
        model = Localization
        
class LocalizationAdmin(ImportExportModelAdmin):
    resource_class = LocalizationResource
    
    # These must be here, inside the Admin class
    list_display = ('id', 'key_name', )
    search_fields = ('id', 'key_name',)
      
admin.site.register(Localization, LocalizationAdmin)

# MigrationHistory AdminPannel
class MigrationHistoryResource(resources.ModelResource):
    
    class Meta:
        model = MigrationHistory
        
class MigrationHistoryAdmin(ImportExportModelAdmin):
    resource_class = MigrationHistoryResource
    
    # These must be here, inside the Admin class
    list_display = ('migration_id', 'voter','from_constituency','to_constituency', )
    search_fields = ('migration_id', 'voter','from_constituency','to_constituency')
      
admin.site.register(MigrationHistory, MigrationHistoryAdmin)

# BlacklistedVoter AdminPannel
class BlacklistedVoterResource(resources.ModelResource):
    
    class Meta:
        model = BlacklistedVoter
        
class BlacklistedVoterAdmin(ImportExportModelAdmin):
    resource_class = BlacklistedVoterResource
    
    # These must be here, inside the Admin class
    list_display = ('id', 'voter', )
    search_fields = ('id', 'voter',)
      
admin.site.register(BlacklistedVoter, BlacklistedVoterAdmin)

# LoginLog AdminPannel
class LoginLogResource(resources.ModelResource):
    
    class Meta:
        model = LoginLog
        
class LoginLogAdmin(ImportExportModelAdmin):
    resource_class = LoginLogResource
    
    # These must be here, inside the Admin class
    list_display = ('id', 'admin', )
    search_fields = ('id', 'admin',)
      
admin.site.register(LoginLog, LoginLogAdmin)


# TempVoter AdminPannel
class TempVoterResource(resources.ModelResource):
    
    class Meta:
        model = TempVoter
        
class TempVoterAdmin(ImportExportModelAdmin):
    resource_class = TempVoterResource
    
    # These must be here, inside the Admin class
    list_display = ('batch_id', 'full_name', )
    search_fields = ('batch_id', 'constituency_name',)
      
admin.site.register(TempVoter, TempVoterAdmin)