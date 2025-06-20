import * as yup from 'yup';

export const contractUploadSchema = yup.object({
  files: yup.array()
    .min(1, 'At least one contract file is required')
    .of(yup.mixed()
      .test('fileType', 'Only PDF, DOCX, and TXT files are allowed', 
        value => ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'].includes(value.type))
      .test('fileSize', 'File size must be less than 10MB', 
        value => value.size <= 10 * 1024 * 1024)
    )
});

export const employeeContractSchema = yup.object({
    employeeId: yup.string().required('Employee ID is required'),
    basicSalary: yup.number().positive().required('Basic salary is required'),
    hra: yup.number().min(0, 'HRA cannot be negative'),
    lta: yup.number().min(0, 'LTA cannot be negative'),
    variablePay: yup.number().min(0, 'Variable pay cannot be negative'),
    pfApplicable: yup.boolean(),
    gratuityApplicable: yup.boolean()
}); 