# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProfilePayNumber'
        db.create_table(u'users_profilepaynumber', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='profile_pay_number', null=True, to=orm['users.Profile'])),
            ('paymethod', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='paymethod_pay_number', null=True, to=orm['currency.PaymentMethod'])),
        ))
        db.send_create_signal(u'users', ['ProfilePayNumber'])


    def backwards(self, orm):
        # Deleting model 'ProfilePayNumber'
        db.delete_table(u'users_profilepaynumber')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'currency.paymentmethod': {
            'Meta': {'object_name': 'PaymentMethod'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'bank': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'commission': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '5', 'decimal_places': '2'}),
            'description_bank': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'disable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_user_bank': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '8'}),
            'max_commission': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '8'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'min_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '8'}),
            'min_commission': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '8'}),
            'valuta': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payment_method'", 'to': u"orm['currency.Valuta']"})
        },
        u'currency.typepair': {
            'Meta': {'unique_together': "(('left', 'right'),)", 'object_name': 'TypePair'},
            'commission': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '5', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'left_right'", 'to': u"orm['currency.Valuta']"}),
            'right': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'funds_right'", 'to': u"orm['currency.Valuta']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'currency.valuta': {
            'Meta': {'object_name': 'Valuta'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'users.addressbook': {
            'Meta': {'object_name': 'AddressBook'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'users.profile': {
            'Meta': {'object_name': 'Profile'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'pair': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['currency.TypePair']", 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        u'users.profilebalance': {
            'Meta': {'object_name': 'ProfileBalance'},
            'accept': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'action': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'bank': ('django.db.models.fields.TextField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'cancel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'commission': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '5', 'decimal_places': '2'}),
            'confirm': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_commission': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '8'}),
            'min_commission': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '8'}),
            'paymethod': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['currency.PaymentMethod']"}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Profile']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'user_bank': ('django.db.models.fields.TextField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '8'}),
            'valuta': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['currency.Valuta']"})
        },
        u'users.profilepaynumber': {
            'Meta': {'object_name': 'ProfilePayNumber'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'paymethod': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paymethod_pay_number'", 'null': 'True', 'to': u"orm['currency.PaymentMethod']"}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'profile_pay_number'", 'null': 'True', 'to': u"orm['users.Profile']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        },
        u'users.profilerole': {
            'Meta': {'unique_together': "(('profile', 'role'),)", 'object_name': 'ProfileRole'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Profile']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        }
    }

    complete_apps = ['users']