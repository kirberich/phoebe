from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class MultiTableMixin(models.Model):
    """ Classes that use multi-table inheritance get a few helper functions for accessing parent and child classes """
    class Meta:
        abstract = True

    parent_name = None
    child_name = models.CharField(max_length=200, blank=True, null=True)

    def get_child(self):
        try: return getattr(self,self.child_name.lower())
        except: return self

    def get_parent(self):
        if not self.parent_name: return self
        try: return getattr(self, self.parent_name.lower()+"_ptr")
        except: return self


@receiver(post_save)
def multi_table_mixin_set_parent(sender, **kwargs):
    instance = kwargs['instance']
    if issubclass(sender, MultiTableMixin):
        if kwargs["created"]:
            parent = instance.get_parent()
            parent.child_name = instance.__class__.__name__
            models.Model.save(parent)
