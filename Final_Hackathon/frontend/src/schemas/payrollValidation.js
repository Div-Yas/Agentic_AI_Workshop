import * as yup from 'yup';

export const payrollProcessSchema = yup.object({
  month: yup.string().required('Month is required'),
  year: yup.number().required('Year is required'),
  employees: yup.array().min(1, 'Select at least one employee'),
  effectiveDate: yup.date().required('Effective date is required')
}); 