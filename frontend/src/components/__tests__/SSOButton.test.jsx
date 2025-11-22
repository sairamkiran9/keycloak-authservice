import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import SSOButton from '../SSOButton';

describe('SSOButton', () => {
  const mockProvider = {
    id: 'google',
    name: 'Google',
    displayName: 'Continue with Google'
  };

  const mockOnClick = vi.fn();

  beforeEach(() => {
    mockOnClick.mockClear();
  });

  it('renders Google SSO button correctly', () => {
    render(
      <SSOButton 
        provider={mockProvider} 
        onClick={mockOnClick} 
        loading={false} 
      />
    );

    expect(screen.getByText('Continue with Google')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('calls onClick with provider id when clicked', () => {
    render(
      <SSOButton 
        provider={mockProvider} 
        onClick={mockOnClick} 
        loading={false} 
      />
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(mockOnClick).toHaveBeenCalledTimes(1);
    expect(mockOnClick).toHaveBeenCalledWith('google');
  });

  it('is disabled when loading', () => {
    render(
      <SSOButton 
        provider={mockProvider} 
        onClick={mockOnClick} 
        loading={true} 
      />
    );

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  it('does not call onClick when disabled', () => {
    render(
      <SSOButton 
        provider={mockProvider} 
        onClick={mockOnClick} 
        loading={true} 
      />
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(mockOnClick).not.toHaveBeenCalled();
  });

  it('contains Google icon SVG', () => {
    render(
      <SSOButton 
        provider={mockProvider} 
        onClick={mockOnClick} 
        loading={false} 
      />
    );

    const svg = screen.getByRole('button').querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveAttribute('width', '18');
    expect(svg).toHaveAttribute('height', '18');
  });

  it('has correct styling classes', () => {
    render(
      <SSOButton 
        provider={mockProvider} 
        onClick={mockOnClick} 
        loading={false} 
      />
    );

    const button = screen.getByRole('button');
    expect(button).toHaveStyle({
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    });
  });
});