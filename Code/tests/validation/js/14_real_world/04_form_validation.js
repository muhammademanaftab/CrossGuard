/**
 * Real-World Form Validation
 * Common form handling patterns
 *
 * Expected features: const, let, arrow-functions, queryselector,
 * classlist, dataset, addeventlistener, constraint-validation,
 * input-event, fetch, json, promises, template-literals
 */

'use strict';

class FormValidator {
    constructor(formSelector) {
        this.form = document.querySelector(formSelector);
        this.fields = new Map();
        this.errors = new Map();

        if (this.form) {
            this.init();
        }
    }

    init() {
        // Find all form fields
        this.form.querySelectorAll('input, select, textarea').forEach(field => {
            const name = field.name;
            if (name) {
                this.fields.set(name, field);
                this.setupFieldListeners(field);
            }
        });

        // Form submit handler
        this.form.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (this.validate()) {
                await this.submit();
            }
        });
    }

    setupFieldListeners(field) {
        // Real-time validation on input
        field.addEventListener('input', (e) => {
            this.validateField(field);
            this.updateFieldUI(field);
        });

        // Validate on blur
        field.addEventListener('blur', () => {
            this.validateField(field);
            this.updateFieldUI(field);
        });

        // Clear errors on focus
        field.addEventListener('focus', () => {
            field.classList.remove('error');
            this.clearFieldError(field);
        });
    }

    validateField(field) {
        const value = field.value.trim();
        const name = field.name;
        let error = null;

        // Check HTML5 validity
        if (!field.validity.valid) {
            if (field.validity.valueMissing) {
                error = `${field.dataset.label || name} is required`;
            } else if (field.validity.typeMismatch) {
                error = `Please enter a valid ${field.type}`;
            } else if (field.validity.patternMismatch) {
                error = field.dataset.patternError || 'Invalid format';
            } else if (field.validity.tooShort) {
                error = `Must be at least ${field.minLength} characters`;
            } else if (field.validity.tooLong) {
                error = `Must be no more than ${field.maxLength} characters`;
            } else if (field.validity.rangeUnderflow) {
                error = `Must be at least ${field.min}`;
            } else if (field.validity.rangeOverflow) {
                error = `Must be no more than ${field.max}`;
            }
        }

        // Custom validations
        if (!error && field.dataset.validate) {
            error = this.runCustomValidation(field, value);
        }

        if (error) {
            this.errors.set(name, error);
            field.setCustomValidity(error);
        } else {
            this.errors.delete(name);
            field.setCustomValidity('');
        }

        return !error;
    }

    runCustomValidation(field, value) {
        const rules = field.dataset.validate.split(' ');

        for (const rule of rules) {
            switch (rule) {
                case 'email':
                    if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                        return 'Please enter a valid email address';
                    }
                    break;

                case 'phone':
                    if (value && !/^\+?[\d\s\-()]+$/.test(value)) {
                        return 'Please enter a valid phone number';
                    }
                    break;

                case 'match':
                    const matchField = this.fields.get(field.dataset.matchField);
                    if (matchField && value !== matchField.value) {
                        return `Must match ${matchField.dataset.label || matchField.name}`;
                    }
                    break;

                case 'strong-password':
                    if (value.length < 8) return 'Password must be at least 8 characters';
                    if (!/[A-Z]/.test(value)) return 'Password must include uppercase';
                    if (!/[a-z]/.test(value)) return 'Password must include lowercase';
                    if (!/[0-9]/.test(value)) return 'Password must include a number';
                    break;
            }
        }

        return null;
    }

    updateFieldUI(field) {
        const error = this.errors.get(field.name);
        const errorEl = this.form.querySelector(`[data-error-for="${field.name}"]`);

        if (error) {
            field.classList.add('error');
            field.classList.remove('valid');
            if (errorEl) {
                errorEl.textContent = error;
                errorEl.hidden = false;
            }
        } else if (field.value) {
            field.classList.remove('error');
            field.classList.add('valid');
            if (errorEl) {
                errorEl.textContent = '';
                errorEl.hidden = true;
            }
        }
    }

    clearFieldError(field) {
        const errorEl = this.form.querySelector(`[data-error-for="${field.name}"]`);
        if (errorEl) {
            errorEl.textContent = '';
        }
    }

    validate() {
        this.errors.clear();
        let isValid = true;

        this.fields.forEach((field) => {
            if (!this.validateField(field)) {
                isValid = false;
            }
            this.updateFieldUI(field);
        });

        if (!isValid) {
            // Focus first error field
            const firstError = this.form.querySelector('.error');
            if (firstError) {
                firstError.focus();
            }
        }

        return isValid;
    }

    async submit() {
        const submitBtn = this.form.querySelector('[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');

        const formData = new FormData(this.form);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch(this.form.action || '/api/submit', {
                method: this.form.method || 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                this.showSuccess('Form submitted successfully!');
                this.form.reset();
            } else {
                this.showError(result.message || 'Submission failed');

                // Show server-side validation errors
                if (result.errors) {
                    Object.entries(result.errors).forEach(([field, message]) => {
                        this.errors.set(field, message);
                        const fieldEl = this.fields.get(field);
                        if (fieldEl) this.updateFieldUI(fieldEl);
                    });
                }
            }
        } catch (error) {
            console.error('Submit error:', error);
            this.showError('Network error. Please try again.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
        }
    }

    showSuccess(message) {
        const alert = document.createElement('div');
        alert.className = 'alert success';
        alert.textContent = message;
        this.form.prepend(alert);
        setTimeout(() => alert.remove(), 5000);
    }

    showError(message) {
        const alert = document.createElement('div');
        alert.className = 'alert error';
        alert.textContent = message;
        this.form.prepend(alert);
        setTimeout(() => alert.remove(), 5000);
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all forms with data-validate attribute
    document.querySelectorAll('form[data-validate]').forEach(form => {
        new FormValidator(`#${form.id}`);
    });
});
