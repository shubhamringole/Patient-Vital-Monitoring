



<img width="764" height="310" alt="PatientVitalMonitoring drawio" src="https://github.com/user-attachments/assets/36b1cac5-81e3-4253-bb57-339b511c60ba" />




python streaming_medallion_pipeline.py \
  --runner DataflowRunner \
  --region us-east1 \
  --worker_machine_type=e2-small \
  --num_workers=1 \
  --max_num_workers=1 \
  --streaming


git init
git remote add origin https://github.com/shubhamringole/Patient-Vital-Monitoring.git
git add .
git commit -m "Initial commit - streaming medallion pipeline"
git branch -M main
git push -u origin main
