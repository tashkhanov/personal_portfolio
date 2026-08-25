import os
import io
from PIL import Image
from django.core.management.base import BaseCommand
from django.conf import settings
from portfolio.models import Certificate, Project, ProjectImage, Service

# We conditionally import SiteSettings to prevent crashing if it doesn't exist
try:
    from portfolio.models import SiteSettings
except ImportError:
    SiteSettings = None

class Command(BaseCommand):
    help = 'Optimizes ALL images in the media folder to WebP and updates the DB'

    def update_db_records(self, old_rel_path, new_rel_path):
        old_rel_path = old_rel_path.replace('\\\\', '/')
        new_rel_path = new_rel_path.replace('\\\\', '/')
        
        for model in [Certificate, Project, ProjectImage, Service]:
            try:
                for obj in model.objects.all():
                    if obj.image and obj.image.name.replace('\\\\', '/') == old_rel_path:
                        obj.image.name = new_rel_path
                        obj.save(update_fields=['image'])
            except Exception:
                pass
                    
        if SiteSettings is not None:
            try:
                for obj in SiteSettings.objects.all():
                    updated = False
                    if hasattr(obj, 'og_image') and obj.og_image and obj.og_image.name.replace('\\\\', '/') == old_rel_path:
                        obj.og_image.name = new_rel_path
                        updated = True
                    if hasattr(obj, 'portrait') and obj.portrait and obj.portrait.name.replace('\\\\', '/') == old_rel_path:
                        obj.portrait.name = new_rel_path
                        updated = True
                    if updated:
                        obj.save()
            except Exception:
                pass

    def handle(self, *args, **kwargs):
        media_root = settings.MEDIA_ROOT
        self.stdout.write(f'Scanning media directory: {media_root}')
        
        count = 0
        for root, dirs, files in os.walk(media_root):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png']:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, media_root)
                    
                    self.stdout.write(f'Converting: {rel_path}')
                    try:
                        img = Image.open(full_path)
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')
                            
                        max_width = 1920
                        if img.width > max_width:
                            ratio = max_width / img.width
                            new_height = int(img.height * ratio)
                            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                        
                        base_name = os.path.splitext(file)[0]
                        if len(base_name) > 50:
                            import hashlib
                            base_name = hashlib.md5(base_name.encode('utf-8')).hexdigest()[:15]
                        new_file = base_name + '.webp'
                        new_full_path = os.path.join(root, new_file)
                        new_rel_path = os.path.relpath(new_full_path, media_root)
                        
                        output = io.BytesIO()
                        img.save(output, format='WEBP', quality=85)
                        with open(new_full_path, 'wb') as f:
                            f.write(output.getvalue())
                            
                        img.close()
                        os.remove(full_path)
                        
                        self.update_db_records(rel_path, new_rel_path)
                        
                        count += 1
                        self.stdout.write(self.style.SUCCESS('  -> Success!'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  -> Error: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Done! Converted and cleaned up {count} images.'))
