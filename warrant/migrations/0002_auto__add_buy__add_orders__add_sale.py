# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Buy'
        db.create_table(u'warrant_buy', (
            (u'orders_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['warrant.Orders'], unique=True, primary_key=True)),
            ('sale', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sale_sale', null=True, to=orm['warrant.Sale'])),
        ))
        db.send_create_signal(u'warrant', ['Buy'])

        # Adding model 'Orders'
        db.create_table(u'warrant_orders', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
            ('commission', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=5, decimal_places=2)),
            ('pair', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'warrant_orders_related', to=orm['currency.TypePair'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=8)),
            ('rate', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=8)),
            ('cancel', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('completed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'warrant', ['Orders'])

        # Adding model 'Sale'
        db.create_table(u'warrant_sale', (
            (u'orders_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['warrant.Orders'], unique=True, primary_key=True)),
            ('buy', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='buy_buy', null=True, to=orm['warrant.Buy'])),
        ))
        db.send_create_signal(u'warrant', ['Sale'])


    def backwards(self, orm):
        # Deleting model 'Buy'
        db.delete_table(u'warrant_buy')

        # Deleting model 'Orders'
        db.delete_table(u'warrant_orders')

        # Deleting model 'Sale'
        db.delete_table(u'warrant_sale')


    models = {
        u'currency.typepair': {
            'Meta': {'unique_together': "(('left', 'right'),)", 'object_name': 'TypePair'},
            'commission': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '5', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'left_right'", 'to': u"orm['currency.Valuta']"}),
            'right': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'funds_right'", 'to': u"orm['currency.Valuta']"})
        },
        u'currency.valuta': {
            'Meta': {'object_name': 'Valuta'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'warrant.buy': {
            'Meta': {'object_name': 'Buy', '_ormbases': [u'warrant.Orders']},
            u'orders_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['warrant.Orders']", 'unique': 'True', 'primary_key': 'True'}),
            'sale': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sale_sale'", 'null': 'True', 'to': u"orm['warrant.Sale']"})
        },
        u'warrant.orders': {
            'Meta': {'object_name': 'Orders'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '8'}),
            'cancel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'commission': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '5', 'decimal_places': '2'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pair': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'warrant_orders_related'", 'to': u"orm['currency.TypePair']"}),
            'rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '8'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        },
        u'warrant.sale': {
            'Meta': {'object_name': 'Sale', '_ormbases': [u'warrant.Orders']},
            'buy': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'buy_buy'", 'null': 'True', 'to': u"orm['warrant.Buy']"}),
            u'orders_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['warrant.Orders']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['warrant']