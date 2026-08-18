-- Governorate set: CAPMAS administrative divisions. Codes: ISO 3166-2:EG.
insert into public.locations (country_code,location_type,official_code,name_en,name_ar,slug_en,slug_ar)
values ('EG','country','EG','Egypt','مصر','egypt','مصر');

with country as (select id from public.locations where official_code='EG')
insert into public.locations(parent_id,country_code,location_type,official_code,name_en,name_ar,slug_en,slug_ar)
select country.id,'EG','governorate',v.code,v.name_en,v.name_ar,v.slug_en,v.slug_ar from country cross join (values
('EG-ALX','Alexandria','الإسكندرية','alexandria','الإسكندرية'),
('EG-ASN','Aswan','أسوان','aswan','أسوان'),('EG-AST','Asyut','أسيوط','asyut','أسيوط'),
('EG-BA','Red Sea','البحر الأحمر','red-sea','البحر-الأحمر'),('EG-BH','Beheira','البحيرة','beheira','البحيرة'),
('EG-BNS','Beni Suef','بني سويف','beni-suef','بني-سويف'),('EG-C','Cairo','القاهرة','cairo','القاهرة'),
('EG-DK','Dakahlia','الدقهلية','dakahlia','الدقهلية'),('EG-DT','Damietta','دمياط','damietta','دمياط'),
('EG-FYM','Faiyum','الفيوم','faiyum','الفيوم'),('EG-GH','Gharbia','الغربية','gharbia','الغربية'),
('EG-GZ','Giza','الجيزة','giza','الجيزة'),('EG-IS','Ismailia','الإسماعيلية','ismailia','الإسماعيلية'),
('EG-JS','South Sinai','جنوب سيناء','south-sinai','جنوب-سيناء'),('EG-KB','Qalyubia','القليوبية','qalyubia','القليوبية'),
('EG-KFS','Kafr El Sheikh','كفر الشيخ','kafr-el-sheikh','كفر-الشيخ'),('EG-KN','Qena','قنا','qena','قنا'),
('EG-LX','Luxor','الأقصر','luxor','الأقصر'),('EG-MN','Minya','المنيا','minya','المنيا'),
('EG-MNF','Monufia','المنوفية','monufia','المنوفية'),('EG-MT','Matrouh','مطروح','matrouh','مطروح'),
('EG-PTS','Port Said','بورسعيد','port-said','بورسعيد'),('EG-SHG','Sohag','سوهاج','sohag','سوهاج'),
('EG-SHR','Sharqia','الشرقية','sharqia','الشرقية'),('EG-SIN','North Sinai','شمال سيناء','north-sinai','شمال-سيناء'),
('EG-SUZ','Suez','السويس','suez','السويس'),('EG-WAD','New Valley','الوادي الجديد','new-valley','الوادي-الجديد')
) as v(code,name_en,name_ar,slug_en,slug_ar);

insert into public.institution_types(code,label_en,label_ar,slug_en,slug_ar,sort_order) values
('nursery','Nursery / Preschool','حضانة / روضة','nursery','حضانة',10),('school','School','مدرسة','school','مدرسة',20),
('university','University','جامعة','university','جامعة',30),('higher_institute','Higher Institute','معهد عالٍ','higher-institute','معهد-عال',40),
('academy','Academy','أكاديمية','academy','أكاديمية',50),('technological_institution','Technological Institution','مؤسسة تكنولوجية','technological-institution','مؤسسة-تكنولوجية',60),
('foreign_university_branch','Foreign University Branch','فرع جامعة أجنبية','foreign-university-branch','فرع-جامعة-أجنبية',70);
insert into public.ownership_types(code,label_en,label_ar,slug_en,slug_ar,sort_order) values
('public','Public','حكومي','public','حكومي',10),('private','Private','خاص','private','خاص',20),('national_nonprofit','National Nonprofit','أهلية غير هادفة للربح','national-nonprofit','أهلية-غير-هادفة-للربح',30),('international','International / Foreign','دولي / أجنبي','international','دولي',40);
insert into public.education_models(code,label_en,label_ar,slug_en,slug_ar,sort_order) values
('coeducational','Coeducational','مختلط','coeducational','مختلط',10),('boys','Boys','بنين','boys','بنين',20),('girls','Girls','بنات','girls','بنات',30),('special_education','Special Education','تربية خاصة','special-education','تربية-خاصة',40);
insert into public.education_levels(code,label_en,label_ar,slug_en,slug_ar,sort_order) values
('early_years','Early Years','الطفولة المبكرة','early-years','الطفولة-المبكرة',10),('primary','Primary','الابتدائي','primary','الابتدائي',20),('preparatory','Preparatory','الإعدادي','preparatory','الإعدادي',30),('secondary','Secondary','الثانوي','secondary','الثانوي',40),('undergraduate','Undergraduate','البكالوريوس / الليسانس','undergraduate','المرحلة-الجامعية',50),('postgraduate','Postgraduate','الدراسات العليا','postgraduate','الدراسات-العليا',60);
insert into public.curricula(code,label_en,label_ar,slug_en,slug_ar,sort_order) values
('egyptian_national','Egyptian National','المناهج المصرية','egyptian-national','المناهج-المصرية',10),('british','British','البريطاني','british','البريطاني',20),('american','American','الأمريكي','american','الأمريكي',30),('ib','International Baccalaureate','البكالوريا الدولية','international-baccalaureate','البكالوريا-الدولية',40),('french','French','الفرنسي','french','الفرنسي',50),('german','German','الألماني','german','الألماني',60);
insert into public.languages(code,label_en,label_ar,slug_en,slug_ar,sort_order) values
('ar','Arabic','العربية','arabic','العربية',10),('en','English','الإنجليزية','english','الإنجليزية',20),('fr','French','الفرنسية','french','الفرنسية',30),('de','German','الألمانية','german','الألمانية',40);
insert into public.certificates(code,label_en,label_ar,slug_en,slug_ar,sort_order) values
('thanaweya_amma','Thanaweya Amma','الثانوية العامة','thanaweya-amma','الثانوية-العامة',10),('igcse','IGCSE','الشهادة الدولية العامة للتعليم الثانوي','igcse','igcse',20),('american_diploma','American Diploma','الدبلومة الأمريكية','american-diploma','الدبلومة-الأمريكية',30),('ib_diploma','IB Diploma','دبلومة البكالوريا الدولية','ib-diploma','دبلومة-البكالوريا-الدولية',40);
insert into public.accreditation_bodies(code,label_en,label_ar,slug_en,slug_ar,sort_order) values
('other_verified','Other verified accreditation body','جهة اعتماد أخرى موثقة','other-verified','جهة-اعتماد-أخرى',100);
insert into public.facilities(code,label_en,label_ar,slug_en,slug_ar,sort_order) values
('library','Library','مكتبة','library','مكتبة',10),('laboratory','Laboratory','معمل','laboratory','معمل',20),('sports','Sports Facilities','منشآت رياضية','sports-facilities','منشآت-رياضية',30),('transport','Transport','نقل مدرسي','transport','نقل-مدرسي',40);
